from urllib.parse import quote

from aegis.tools.base import Tool, ToolResult
from aegis.tools.http import HTTPRequestTool


class SSRFValidator:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def execute(
        self,
        path: str,
        parameter: str,
    ) -> ToolResult:
        internal_url = (
            "http://127.0.0.1:4000/"
            "internal-secret"
        )

        encoded_url = quote(
            internal_url,
            safe="",
        )

        target_path = (
            f"{path}?{parameter}={encoded_url}"
        )

        try:
            import requests

            response = requests.get(
                self.base_url + target_path,
                timeout=5,
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=str(error),
            )

        marker = "AEGIS_SSRF_7f3c91"

        confirmed = (
            response.status_code == 200
            and marker in response.text
        )

        return ToolResult(
            success=True,
            output={
                "confirmed": confirmed,
                "vulnerability": "ssrf",
                "path": path,
                "parameter": parameter,
                "internal_url": internal_url,
                "status_code": response.status_code,
                "response_body": response.text[:1000],
                "marker": marker,
                "reason": (
                    "The controlled internal service "
                    "was reached through the user-controlled "
                    "URL parameter."
                    if confirmed
                    else
                    "The controlled internal service "
                    "was not reached."
                ),
            },
        )