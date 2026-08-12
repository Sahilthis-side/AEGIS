import time
import urllib.request
from pathlib import Path

import docker
from docker.errors import DockerException, NotFound


class DockerSandbox:

    def __init__(self, target_info):
        self.target_info = target_info
        self.target_path = Path(target_info.path).resolve()

        self.client = docker.from_env()
        self.container = None
        self.host_port = None

        self.image = self._select_image()

    # ==========================================================
    # RUNTIME SELECTION
    # ==========================================================

    def _select_image(self):
        language = self.target_info.language.lower()

        if language == "javascript/typescript":
            return "node:22-bookworm"

        if language == "python":
            return "python:3.12-bookworm"

        if language == "java":
            return "maven:3.9-eclipse-temurin-21"

        raise RuntimeError(
            f"Unsupported target language: "
            f"{self.target_info.language}"
        )

    # ==========================================================
    # DOCKER CONNECTION
    # ==========================================================

    def check_connection(self):
        try:
            self.client.ping()
            return True

        except DockerException as e:
            raise RuntimeError(
                f"Could not connect to Docker: {e}"
            ) from e

    # ==========================================================
    # START SANDBOX
    # ==========================================================

    def start(self):
        """Create the isolated Docker container."""

        self.check_connection()

        print("[+] Docker connection established")
        print(f"[+] Runtime image: {self.image}")
        print("[+] Creating sandbox...")

        self.container = self.client.containers.run(
            image=self.image,
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

        port_info = (
            self.container.attrs[
                "NetworkSettings"
            ]["Ports"]
        )

        mapping = port_info.get("3000/tcp")

        if not mapping:
            raise RuntimeError(
                "Docker did not expose port 3000."
            )

        self.host_port = int(
            mapping[0]["HostPort"]
        )

        print(
            f"[+] Sandbox started: "
            f"{self.container.name}"
        )

        print(
            f"[+] Port mapping: "
            f"localhost:{self.host_port} -> 3000"
        )

        return self.container

    # ==========================================================
    # DEPENDENCIES
    # ==========================================================

    def install_dependencies(self):
        """Install dependencies using the target's package manager."""

        print("[+] Installing dependencies...")

        package_manager = (
            self.target_info.package_manager.lower()
        )

        # ------------------------------------------------------
        # Node.js
        # ------------------------------------------------------

        if package_manager == "npm":

            command = (
                "npm install --ignore-scripts"
            )

        # ------------------------------------------------------
        # Python
        # ------------------------------------------------------

        elif package_manager == "pip":

            if (
                (self.target_path / "requirements.txt")
                .exists()
            ):
                command = (
                    "pip install --no-cache-dir "
                    "-r requirements.txt"
                )

            elif (
                (self.target_path / "pyproject.toml")
                .exists()
            ):
                command = (
                    "pip install --no-cache-dir ."
                )

            else:
                raise RuntimeError(
                    "Python target has no "
                    "requirements.txt or pyproject.toml."
                )

        # ------------------------------------------------------
        # Java / Maven
        # ------------------------------------------------------

        elif package_manager == "maven":

            # Maven is already installed in the
            # maven Docker image.
            command = (
                "mvn -B dependency:go-offline"
            )

        else:

            raise RuntimeError(
                f"Unsupported package manager: "
                f"{self.target_info.package_manager}"
            )

        exit_code, output = self.execute(
            command
        )

        if exit_code != 0:

            raise RuntimeError(
                f"Dependency installation failed:\n"
                f"{output}"
            )

        print("[+] Dependencies installed")

    # ==========================================================
    # START APPLICATION
    # ==========================================================

    def start_application(self):
        """Start the target application."""

        print("[+] Starting application...")

        command = self.target_info.start_command

        if not command:
            raise RuntimeError(
                "No start command detected for "
                f"{self.target_info.language} target."
            )

        print(f"[+] Command: {command}")

        result = self.container.exec_run(
            [
                "bash",
                "-c",
                command,
            ],
            detach=True,
        )

        if result is None:
            raise RuntimeError(
                "Failed to start application."
            )

        print(
            "[+] Application process started"
        )

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def wait_for_health(
        self,
        timeout: int = 30,
    ):
        """Wait until the application responds."""

        if self.host_port is None:
            raise RuntimeError(
                "Host port is not available."
            )

        health_paths = [
            "/health",
            "/",
        ]

        print(
            "[+] Waiting for application..."
        )

        start_time = time.time()

        while (
            time.time() - start_time
            < timeout
        ):

            for path in health_paths:

                url = (
                    f"http://127.0.0.1:"
                    f"{self.host_port}"
                    f"{path}"
                )

                try:

                    with urllib.request.urlopen(
                        url,
                        timeout=2,
                    ) as response:

                        if 200 <= response.status < 500:

                            print(
                                "[+] Application "
                                f"responded successfully "
                                f"at {path}"
                            )

                            return True

                except Exception:
                    pass

            time.sleep(1)

        raise RuntimeError(
            "Application did not become "
            f"healthy within {timeout} seconds."
        )

    # ==========================================================
    # EXECUTE COMMAND
    # ==========================================================

    def execute(self, command: str):
        """Execute a command inside the sandbox."""

        if self.container is None:
            raise RuntimeError(
                "Sandbox is not running."
            )

        result = self.container.exec_run(
            [
                "bash",
                "-c",
                command,
            ]
        )

        output = result.output.decode(
            "utf-8",
            errors="replace",
        )

        return (
            result.exit_code,
            output,
        )

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):
        """Stop and remove the sandbox."""

        if self.container is None:
            return

        try:

            print(
                "[+] Stopping sandbox..."
            )

            self.container.stop(
                timeout=5
            )

            self.container.remove()

            print(
                "[+] Sandbox removed"
            )

        except NotFound:
            pass

        finally:

            self.container = None
            self.host_port = None