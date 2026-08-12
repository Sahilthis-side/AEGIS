from aegis.tools.base import Tool, ToolResult


class ToolRegistry:

    def __init__(self):

        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:

        if name not in self._tools:

            raise KeyError(
                f"Unknown tool: {name}"
            )

        return self._tools[name]

    def execute(
        self,
        name: str,
        **kwargs,
    ) -> ToolResult:

        tool = self.get(name)

        return tool.execute(**kwargs)

    def list_tools(self):

        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools.values()
        ]

    def schemas(self):

        return [
            {
                "type": "function",
                "function": {
                    "name": "security_test",
                    "description": (
                        "Run a deterministic vulnerability "
                        "validator against the authorized "
                        "sandbox application."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "vulnerability": {
                                "type": "string",
                                "enum": [
                                    "sql_injection",
                                    "xss",
                                    "ssrf",
                                    "idor",
                                    "path_traversal",
                                    "command_injection",
                                    "authentication_bypass",
                                ],
                            },
                            "path": {
                                "type": "string",
                            },
                            "parameter": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "vulnerability",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_source_files",
                    "description": (
                        "List source-code files in the authorized "
                        "application. Use this before read_source "
                        "when the relevant filename is unknown."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_source",
                    "description": (
                        "Read source code from the authorized "
                        "application. Use this to understand "
                        "how endpoints process user input and "
                        "to identify the root cause of a "
                        "potential vulnerability."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": (
                                    "Relative path to the source "
                                    "file inside the target."
                                ),
                            },
                            "start_line": {
                                "type": "integer",
                                "description": (
                                    "First line to read. "
                                    "Defaults to 1."
                                ),
                            },
                            "end_line": {
                                "type": "integer",
                                "description": (
                                    "Last line to read. "
                                    "Maximum 200 lines per call."
                                ),
                            },
                        },
                        "required": [
                            "path",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "http_request",
                    "description": (
                        "Send an HTTP request to "
                        "the sandboxed application."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string"
                            },
                            "path": {
                                "type": "string"
                            },
                            "headers": {
                                "type": "object"
                            },
                            "params": {
                                "type": "object"
                            },
                            "data": {
                                "type": "string"
                            },
                            "json": {
                                "type": "object"
                            },
                        },
                        "required": [
                            "method",
                            "path",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "record_evidence",
                    "description": (
                        "Record evidence discovered "
                        "during the scan."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "evidence_type": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "data": {
                                "type": "object"
                            },
                        },
                        "required": [
                            "evidence_type",
                            "description",
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "create_finding",
                    "description": (
                        "Create a security finding "
                        "only after sufficient "
                        "validation evidence."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string"
                            },
                            "severity": {
                                "type": "string"
                            },
                            "confidence": {
                                "type": "string"
                            },
                            "endpoint": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "evidence": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                            },
                            "remediation": {
                                "type": "string"
                            },
                        },
                        "required": [
                            "title",
                            "severity",
                            "confidence",
                            "description",
                        ],
                    },
                },
            },
        ]
