from typing import Any

from aegis.security.engine import VulnerabilityEngine


class AttackSurfaceAnalyzer:

    def __init__(self, engine: VulnerabilityEngine):
        self.engine = engine

    def analyze(
        self,
        endpoints: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        candidates = []

        available = set(self.engine.available())

        for endpoint in endpoints:

            method = endpoint.get(
                "method",
                "GET",
            ).upper()

            path = endpoint.get(
                "path",
                "/",
            )

            parameters = endpoint.get(
                "parameters",
                [],
            )

            for parameter in parameters:

                if isinstance(parameter, dict):
                    parameter_name = parameter.get(
                        "name",
                        "",
                    )
                    location = parameter.get(
                        "location",
                        "query",
                    )
                else:
                    parameter_name = str(parameter)
                    location = "query"

                if not parameter_name:
                    continue

                parameter_lower = (
                    parameter_name.lower()
                )
                if "xss" in available:

                    candidates.append({
                        "vulnerability": "xss",
                        "method": method,
                        "path": path,
                        "parameter": parameter_name,
                        "location": location,
                        "reason": (
                            "User-controlled parameter "
                            "may reach HTML output."
                        ),
                    })
                if "sql_injection" in available:

                    candidates.append({
                        "vulnerability": "sql_injection",
                        "method": method,
                        "path": path,
                        "parameter": parameter_name,
                        "location": location,
                        "reason": (
                            "User-controlled parameter "
                            "may influence a database query."
                        ),
                    })
                if "ssrf" in available:

                    url_keywords = (
                        "url",
                        "uri",
                        "link",
                        "redirect",
                        "callback",
                        "target",
                        "dest",
                        "destination",
                    )

                    if any(
                        keyword in parameter_lower
                        for keyword in url_keywords
                    ):

                        candidates.append({
                            "vulnerability": "ssrf",
                            "method": method,
                            "path": path,
                            "parameter": parameter_name,
                            "location": location,
                            "reason": (
                                "Parameter name suggests "
                                "it may accept a URL or "
                                "network destination."
                            ),
                        })
                if "path_traversal" in available:

                    file_keywords = (
                        "file",
                        "path",
                        "filename",
                        "template",
                        "document",
                    )

                    if any(
                        keyword in parameter_lower
                        for keyword in file_keywords
                    ):

                        candidates.append({
                            "vulnerability": "path_traversal",
                            "method": method,
                            "path": path,
                            "parameter": parameter_name,
                            "location": location,
                            "reason": (
                                "Parameter name suggests "
                                "possible filesystem access."
                            ),
                        })

        return candidates