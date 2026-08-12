from typing import Any

from aegis.security.validators.base import (
    VulnerabilityValidator,
)


class ValidatorRegistry:

    def __init__(self):
        self._validators: dict[
            str,
            VulnerabilityValidator,
        ] = {}

    def register(
        self,
        validator: VulnerabilityValidator,
    ):
        self._validators[
            validator.name
        ] = validator

    def get(
        self,
        name: str,
    ) -> VulnerabilityValidator | None:

        return self._validators.get(name)

    def all(self) -> list[VulnerabilityValidator]:

        return list(
            self._validators.values()
        )

    def applicable(
        self,
        endpoint: dict[str, Any],
    ) -> list[VulnerabilityValidator]:

        return [
            validator
            for validator in self._validators.values()
            if validator.can_test(endpoint)
        ]