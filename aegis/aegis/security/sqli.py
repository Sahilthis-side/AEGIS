from aegis.security.base import (
    ValidationResult,
    VulnerabilityValidator,
)

from aegis.tools.sqli import (
    SQLInjectionValidator,
)


class SQLInjectionSecurityValidator(
    VulnerabilityValidator
):

    name = "sql_injection"

    description = (
        "Validate SQL injection against an "
        "authorized application endpoint."
    )

    def __init__(
        self,
        base_url: str,
    ):

        self.validator = (
            SQLInjectionValidator(
                base_url
            )
        )

    def test(
        self,
        path: str,
        parameter: str,
    ) -> ValidationResult:

        result = self.validator.execute(
            path=path,
            parameter=parameter,
        )

        if not result.success:

            return ValidationResult(
                vulnerability=self.name,
                status="insufficient_evidence",
                confidence="none",
                description=(
                    "SQL injection validation "
                    "could not be completed."
                ),
                details={
                    "error": result.error,
                },
            )

        output = result.output

        confirmed = False

        if isinstance(output, dict):

            confirmed = bool(
                output.get(
                    "confirmed",
                    False,
                )
            )

        if confirmed:

            return ValidationResult(
                vulnerability=self.name,
                status="confirmed",
                confidence="high",
                title=(
                    "SQL Injection Vulnerability"
                ),
                description=(
                    "The deterministic SQL injection "
                    "validator confirmed that the "
                    "user-controlled parameter can "
                    "influence the database query."
                ),
                evidence=[
                    str(output),
                ],
                details=output,
                remediation=(
                    "Use parameterized queries or "
                    "prepared statements instead of "
                    "concatenating user input into SQL."
                ),
            )

        return ValidationResult(
            vulnerability=self.name,
            status="not_confirmed",
            confidence="medium",
            title="SQL Injection Not Confirmed",
            description=(
                "The SQL injection validator did "
                "not obtain sufficient evidence."
            ),
            evidence=[
                str(output),
            ],
            details=output,
        )