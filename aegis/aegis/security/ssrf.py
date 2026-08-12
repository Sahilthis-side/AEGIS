from aegis.security.base import (
    ValidationResult,
    VulnerabilityValidator,
)

from aegis.tools.ssrf import SSRFValidator


class SSRFSecurityValidator(
    VulnerabilityValidator
):

    name = "ssrf"

    description = (
        "Validate server-side request forgery "
        "against an authorized sandbox application."
    )

    def __init__(
        self,
        base_url: str,
    ):

        self.validator = SSRFValidator(
            base_url
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
                title="SSRF Validation Error",
                description=(
                    "The SSRF validator could not "
                    "complete the security test."
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
                    "Server-Side Request Forgery "
                    "(SSRF)"
                ),
                description=(
                    "The controlled SSRF validator "
                    "confirmed that user-controlled "
                    "URL input can cause the server "
                    "to access an internal service."
                ),
                evidence=[
                    str(output),
                ],
                details=output,
                remediation=(
                    "Do not allow user-controlled URLs "
                    "to access arbitrary network "
                    "resources. Apply an allowlist of "
                    "permitted destinations and block "
                    "loopback, private, link-local, and "
                    "other internal network addresses."
                ),
            )

        return ValidationResult(
            vulnerability=self.name,
            status="not_confirmed",
            confidence="medium",
            title="SSRF Not Confirmed",
            description=(
                "The SSRF validator did not obtain "
                "sufficient evidence that the server "
                "accessed the controlled internal "
                "resource."
            ),
            evidence=[
                str(output),
            ],
            details=output,
        )