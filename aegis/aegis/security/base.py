from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:

    vulnerability: str

    status: str
    # confirmed
    # not_confirmed
    # insufficient_evidence

    confidence: str = "low"

    title: str = ""

    description: str = ""

    evidence: list[str] = field(
        default_factory=list
    )

    details: dict[str, Any] = field(
        default_factory=dict
    )

    remediation: str = ""


class VulnerabilityValidator(ABC):

    name: str
    description: str

    @abstractmethod
    def test(
        self,
        **kwargs,
    ) -> ValidationResult:
        pass