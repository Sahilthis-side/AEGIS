from typing import Any

import requests

from aegis.tools.base import Tool, ToolResult


class HTTPRequestTool(Tool):

    name = "http_request"

    description = (
        "Send an HTTP request to the sandboxed target."
    )

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def execute(
        self,
        method: str = "GET",
        path: str = "/",
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json: Any = None,
    ) -> ToolResult:

        url = (
            f"{self.base_url}/"
            f"{path.lstrip('/')}"
        )

        try:

            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=10,
            )

            return ToolResult(
                success=True,
                output={
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:10000],
                    "url": response.url,
                },
            )

        except requests.RequestException as e:

            return ToolResult(
                success=False,
                output=None,
                error=str(e),
            )