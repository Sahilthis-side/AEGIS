from aegis.security.base import (
    ValidationResult,
    VulnerabilityValidator,
)

from aegis.tools.path_traversal import (
    PathTraversalValidator,
)


class PathTraversalSecurityValidator(
    VulnerabilityValidator
):

    name = "path_traversal"

    description = (
        "Validate path traversal against an "
        "authorized application endpoint."
    )

    def __init__(
        self,
        base_url: str,
    ):

        self.validator = (
            PathTraversalValidator(
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
                    "Path traversal validation "
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
                    "Path Traversal Vulnerability"
                ),
                description=(
                    "The deterministic path traversal "
                    "validator confirmed that a "
                    "user-controlled parameter can "
                    "access a file outside the "
                    "intended filesystem boundary."
                ),
                evidence=[
                    str(output),
                ],
                details=output,
                remediation=(
                    "Do not construct filesystem paths "
                    "directly from user-controlled input. "
                    "Resolve paths against a fixed base "
                    "directory and verify that the resolved "
                    "path remains inside that directory."
                ),
            )

        return ValidationResult(
            vulnerability=self.name,
            status="not_confirmed",
            confidence="medium",
            title=(
                "Path Traversal Not Confirmed"
            ),
            description=(
                "The path traversal validator did "
                "not obtain sufficient evidence."
            ),
            evidence=[
                str(output),
            ],
            details=output,
        )