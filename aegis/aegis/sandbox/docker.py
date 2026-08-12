import time
import urllib.request
from pathlib import Path

import docker
from docker.errors import DockerException, NotFound


class DockerSandbox:
    def __init__(self, target_path: str):
        self.target_path = Path(target_path).resolve()
        self.client = docker.from_env()
        self.container = None
        self.host_port = None

    def check_connection(self):
        try:
            self.client.ping()
            return True
        except DockerException as e:
            raise RuntimeError(
                f"Could not connect to Docker: {e}"
            ) from e

    def start(self):
        """Create the isolated Docker container."""

        self.check_connection()

        print("[+] Docker connection established")
        print("[+] Creating sandbox...")

        self.container = self.client.containers.run(
            image="node:22-bookworm",
            command="sleep infinity",
            detach=True,
            name=f"aegis-sandbox-{int(time.time())}",
            volumes={
                str(self.target_path): {
                    "bind": "/app",
                    "mode": "rw",
                }
            },
            working_dir="/app",
            ports={
                "3000/tcp": None,
            },
            mem_limit="512m",
            pids_limit=256,
        )
        self.container.reload()

        port_info = self.container.attrs["NetworkSettings"]["Ports"]

        mapping = port_info.get("3000/tcp")

        if not mapping:
            raise RuntimeError("Docker did not expose port 3000.")

        self.host_port = int(mapping[0]["HostPort"])

        print(f"[+] Sandbox started: {self.container.name}")
        print(f"[+] Port mapping: localhost:{self.host_port} -> 3000")

        return self.container

    def install_dependencies(self):
        """Install application dependencies inside the sandbox."""

        print("[+] Installing dependencies...")

        exit_code, output = self.execute(
            "npm install --ignore-scripts"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"npm install failed:\n{output}"
            )

        print("[+] Dependencies installed")

    def start_application(self):
        """Start the target application."""

        print("[+] Starting application...")

        result = self.container.exec_run(
            ["bash", "-c", "npm run dev"],
            detach=True,
        )

        if result is None:
            raise RuntimeError("Failed to start application.")

        print("[+] Application process started")

    def wait_for_health(self, timeout: int = 30):
        """Wait until the application responds over HTTP."""

        if self.host_port is None:
            raise RuntimeError("Host port is not available.")

        url = f"http://127.0.0.1:{self.host_port}/health"

        print("[+] Waiting for application...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                with urllib.request.urlopen(
                    url,
                    timeout=2
                ) as response:

                    if response.status == 200:
                        print(
                            "[+] Application health check passed"
                        )
                        return True

            except Exception:
                pass

            time.sleep(1)

        raise RuntimeError(
            f"Application did not become healthy within "
            f"{timeout} seconds."
        )

    def execute(self, command: str):
        """Execute a command inside the sandbox."""

        if self.container is None:
            raise RuntimeError("Sandbox is not running.")

        result = self.container.exec_run(
            ["bash", "-c", command]
        )

        output = result.output.decode(
            "utf-8",
            errors="replace"
        )

        return result.exit_code, output

    def stop(self):
        """Stop and remove the sandbox."""

        if self.container is None:
            return

        try:
            print("[+] Stopping sandbox...")
            self.container.stop(timeout=5)
            self.container.remove()
            print("[+] Sandbox removed")

        except NotFound:
            pass

        finally:
            self.container = None
            self.host_port = None