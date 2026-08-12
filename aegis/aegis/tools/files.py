from pathlib import Path

from aegis.tools.base import Tool, ToolResult


class ListSourceFilesTool(Tool):

    name = "list_source_files"

    description = (
        "List source files in the authorized "
        "application so the security agent can "
        "identify files relevant to an endpoint."
    )

    EXTENSIONS = {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".py",
        ".java",
        ".go",
        ".rs",
        ".php",
        ".rb",
    }

    IGNORED_DIRS = {
        "node_modules",
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "dist",
        "build",
    }

    def __init__(self, target_path: str):

        self.target_path = Path(
            target_path
        ).resolve()

    def execute(self) -> ToolResult:

        try:

            files = []

            for path in self.target_path.rglob("*"):

                if not path.is_file():
                    continue

                if any(
                    part in self.IGNORED_DIRS
                    for part in path.parts
                ):
                    continue

                if path.suffix.lower() in self.EXTENSIONS:

                    files.append(
                        str(
                            path.relative_to(
                                self.target_path
                            )
                        )
                    )

            files.sort()

            return ToolResult(
                success=True,
                output={
                    "files": files,
                    "count": len(files),
                },
            )

        except Exception as error:

            return ToolResult(
                success=False,
                output=None,
                error=str(error),
            )