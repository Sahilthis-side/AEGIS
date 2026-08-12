from typing import Any

from aegis.security.base import (
    ValidationResult,
    VulnerabilityValidator,
)


class VulnerabilityEngine:

    def __init__(self):

        self.validators: dict[
            str,
            VulnerabilityValidator,
        ] = {}

    def register(
        self,
        validator: VulnerabilityValidator,
    ):

        self.validators[
            validator.name
        ] = validator

    def available(self):

        return list(
            self.validators.keys()
        )

    def test(
        self,
        vulnerability: str,
        **kwargs: Any,
    ) -> ValidationResult:

        validator = self.validators.get(
            vulnerability
        )

        if validator is None:

            return ValidationResult(
                vulnerability=vulnerability,
                status="insufficient_evidence",
                confidence="none",
                title="Unsupported vulnerability type",
                description=(
                    f"No validator is currently "
                    f"registered for '{vulnerability}'."
                ),
            )

        try:

            return validator.test(
                **kwargs
            )

        except Exception as error:

            return ValidationResult(
                vulnerability=vulnerability,
                status="insufficient_evidence",
                confidence="none",
                title="Validator execution error",
                description=(
                    f"The {vulnerability} validator "
                    f"could not complete."
                ),
                details={
                    "error": str(error),
                },
            )