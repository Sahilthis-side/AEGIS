from abc import ABC, abstractmethod
from typing import Any

from aegis.security.base import ValidationResult


class VulnerabilityValidator(ABC):

    name: str = ""
    description: str = ""

    @abstractmethod
    def can_test(
        self,
        endpoint: dict[str, Any],
    ) -> bool:
        """
        Return True when this validator is
        applicable to the endpoint.
        """
        raise NotImplementedError

    @abstractmethod
    def test(
        self,
        endpoint: dict[str, Any],
    ) -> ValidationResult:
        """
        Perform deterministic validation.
        """
        raise NotImplementedError