import requests

from aegis.tools.base import Tool, ToolResult


class PathTraversalValidator(Tool):

    name = "path_traversal_validator"

    description = (
        "Deterministically test an authorized HTTP endpoint "
        "for path traversal."
    )

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def execute(
        self,
        path: str,
        parameter: str,
    ) -> ToolResult:

        url = f"{self.base_url}{path}"

        marker = "AEGIS_PATH_TRAVERSAL_7f3c91"

        payloads = [
            "../private/aegis-secret.txt",
            "../../private/aegis-secret.txt",
            "../../../private/aegis-secret.txt",
            "..\\private\\aegis-secret.txt",
            "..\\..\\private\\aegis-secret.txt",
            "..\\..\\..\\private\\aegis-secret.txt",
        ]

        try:

            baseline_response = requests.get(
                url,
                params={
                    parameter: "hello.txt",
                },
                timeout=5,
            )

            baseline = {
                "status_code": baseline_response.status_code,
                "body_length": len(
                    baseline_response.text
                ),
            }

            for payload in payloads:

                response = requests.get(
                    url,
                    params={
                        parameter: payload,
                    },
                    timeout=5,
                )

                if marker in response.text:

                    return ToolResult(
                        success=True,
                        output={
                            "confirmed": True,
                            "path": path,
                            "parameter": parameter,
                            "payload": payload,
                            "status_code": response.status_code,
                            "baseline": baseline,
                            "evidence": (
                                "The controlled traversal "
                                "marker was retrieved "
                                "outside the intended "
                                "directory."
                            ),
                        },
                    )

            return ToolResult(
                success=True,
                output={
                    "confirmed": False,
                    "path": path,
                    "parameter": parameter,
                    "baseline": baseline,
                    "tested_payloads": payloads,
                    "evidence": (
                        "No controlled traversal "
                        "marker was retrieved."
                    ),
                },
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=str(error),
            )