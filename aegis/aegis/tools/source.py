from pathlib import Path

from aegis.tools.base import Tool, ToolResult


class ReadSourceTool(Tool):

    name = "read_source"

    description = (
        "Read source code from the authorized "
        "application. Use this to understand how "
        "an endpoint processes user-controlled input."
    )

    def __init__(self, target_path: str):

        self.target_path = Path(
            target_path
        ).resolve()

    def execute(
        self,
        path: str,
        start_line: int = 1,
        end_line: int = 200,
    ) -> ToolResult:

        try:

            requested = (
                self.target_path / path
            ).resolve()

            # Prevent escaping the target directory.
            requested.relative_to(
                self.target_path
            )

        except ValueError:

            return ToolResult(
                success=False,
                output=None,
                error=(
                    "Access denied: requested file "
                    "is outside the target directory."
                ),
            )

        if not requested.exists():

            return ToolResult(
                success=False,
                output=None,
                error=(
                    f"File not found: {path}"
                ),
            )

        if not requested.is_file():

            return ToolResult(
                success=False,
                output=None,
                error=(
                    f"Not a file: {path}"
                ),
            )

        # Prevent accidentally dumping enormous files.
        start_line = max(
            1,
            start_line,
        )

        end_line = min(
            start_line + 199,
            end_line,
        )

        try:

            lines = requested.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()

            selected = lines[
                start_line - 1:end_line
            ]

            content = "\n".join(
                f"{start_line + i}: {line}"
                for i, line in enumerate(selected)
            )

            return ToolResult(
                success=True,
                output={
                    "file": str(
                        requested.relative_to(
                            self.target_path
                        )
                    ),
                    "start_line": start_line,
                    "end_line": (
                        start_line
                        + len(selected)
                        - 1
                    ),
                    "content": content,
                },
            )

        except Exception as error:

            return ToolResult(
                success=False,
                output=None,
                error=str(error),
            )