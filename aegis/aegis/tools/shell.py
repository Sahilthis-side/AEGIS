from aegis.sandbox.docker import DockerSandbox
from aegis.tools.base import Tool, ToolResult


class SandboxCommandTool(Tool):

    name = "sandbox_command"

    description = (
        "Execute a command inside the target Docker sandbox."
    )

    def __init__(self, sandbox: DockerSandbox):
        self.sandbox = sandbox

    def execute(self, command: str) -> ToolResult:

        if not command.strip():

            return ToolResult(
                success=False,
                output=None,
                error="Command cannot be empty.",
            )

        try:

            exit_code, output = (
                self.sandbox.execute(command)
            )

            return ToolResult(
                success=exit_code == 0,
                output={
                    "exit_code": exit_code,
                    "stdout": output,
                },
                error=(
                    None
                    if exit_code == 0
                    else "Command returned a non-zero exit code."
                ),
            )

        except Exception as e:

            return ToolResult(
                success=False,
                output=None,
                error=str(e),
            )