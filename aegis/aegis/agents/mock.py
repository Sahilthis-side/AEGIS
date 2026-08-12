from aegis.agents.model import (
    AgentModel,
    AgentResponse,
)


class MockSecurityModel(AgentModel):

    def __init__(self):
        self.step = 0

    def think(
        self,
        context,
        tools,
    ):

        self.step += 1

        endpoints = context.get(
            "endpoints",
            []
        )
        if self.step == 1:

            for endpoint in endpoints:

                if (
                    endpoint["method"] == "GET"
                    and endpoint["parameters"]
                ):

                    parameter = (
                        endpoint["parameters"][0]["name"]
                    )

                    context["test_endpoint"] = (
                        endpoint["path"]
                    )

                    context["test_parameter"] = (
                        parameter
                    )

                    return AgentResponse(
                        message=(
                            "Found a GET endpoint with "
                            "user-controlled input. "
                            "Testing the parameter."
                        ),
                        tool_name="validate_sqli",
                        tool_arguments={
                            "path": endpoint["path"],
                            "parameter": parameter,
                        },
                    )
        if self.step == 2:

            validation = context.get(
                "last_tool_result"
            )

            if validation:

                confirmed = (
                    validation
                    .get("confirmed", False)
                )

                if confirmed:

                    return AgentResponse(
                        message=(
                            "Deterministic validation "
                            "confirmed SQL injection."
                        ),
                        tool_name="create_finding",
                        tool_arguments={
                            "title": "SQL Injection",
                            "severity": "CRITICAL",
                            "confidence": "CONFIRMED",
                            "endpoint": (
                                context.get(
                                    "test_endpoint"
                                )
                            ),
                            "description": (
                                "User-controlled query "
                                "input changes database "
                                "query behavior and "
                                "causes additional "
                                "records to be returned."
                            ),
                            "evidence": [
                                validation.get(
                                    "reason",
                                    "Validator confirmed "
                                    "SQL injection."
                                )
                            ],
                            "remediation": (
                                "Use parameterized "
                                "queries or prepared "
                                "statements instead of "
                                "concatenating user input "
                                "into SQL queries."
                            ),
                        },
                    )

                return AgentResponse(
                    message=(
                        "The SQL injection hypothesis "
                        "was not sufficiently supported "
                        "by deterministic evidence."
                    ),
                    finished=True,
                )
        if self.step == 3:

            return AgentResponse(
                message=(
                    "Security investigation complete."
                ),
                finished=True,
            )

        return AgentResponse(
            message="Investigation complete.",
            finished=True,
        )