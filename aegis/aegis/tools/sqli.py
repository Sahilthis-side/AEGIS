from typing import Any

import requests

from aegis.tools.base import Tool, ToolResult


class SQLInjectionValidator(Tool):

    name = "validate_sqli"

    description = (
        "Test a query parameter for SQL injection "
        "using a baseline request and a controlled "
        "boolean-based test."
    )

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def execute(
        self,
        path: str,
        parameter: str,
    ) -> ToolResult:

        url = (
            f"{self.base_url}/"
            f"{path.lstrip('/')}"
        )

        try:
            baseline = requests.get(
                url,
                params={
                    parameter: "alice"
                },
                timeout=10,
            )
            payload = "' OR '1'='1"

            attack = requests.get(
                url,
                params={
                    parameter: payload
                },
                timeout=10,
            )

            baseline_body = baseline.text
            attack_body = attack.text

            evidence: dict[str, Any] = {
                "url": url,
                "parameter": parameter,
                "payload": payload,
                "baseline": {
                    "status_code": baseline.status_code,
                    "body_length": len(baseline_body),
                },
                "attack": {
                    "status_code": attack.status_code,
                    "body_length": len(attack_body),
                },
            }
            confirmed = False
            reason = ""

            if (
                baseline.status_code == 200
                and attack.status_code == 200
            ):

                try:

                    baseline_json = (
                        baseline.json()
                    )

                    attack_json = (
                        attack.json()
                    )

                    baseline_count = (
                        baseline_json.get("count")
                    )

                    attack_count = (
                        attack_json.get("count")
                    )

                    if (
                        isinstance(baseline_count, int)
                        and isinstance(attack_count, int)
                        and attack_count > baseline_count
                    ):

                        confirmed = True

                        reason = (
                            "The SQL injection test caused "
                            "the application to return more "
                            "database records than the "
                            "baseline request."
                        )

                except ValueError:

                    pass

            if not confirmed:

                reason = (
                    "The controlled SQL injection test "
                    "did not produce sufficient "
                    "deterministic evidence."
                )

            evidence["confirmed"] = confirmed
            evidence["reason"] = reason

            return ToolResult(
                success=True,
                output=evidence,
            )

        except requests.RequestException as e:

            return ToolResult(
                success=False,
                output=None,
                error=str(e),
            )