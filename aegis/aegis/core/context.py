from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    title: str
    severity: str
    confidence: str
    endpoint: str | None = None
    description: str = ""
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""


@dataclass
class Evidence:
    type: str
    description: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanContext:
    target_path: str
    base_url: str | None = None

    language: str | None = None
    framework: str | None = None
    package_manager: str | None = None

    technologies: list[str] = field(
        default_factory=list
    )

    endpoints: list[dict[str, Any]] = field(
        default_factory=list
    )

    links: list[str] = field(
        default_factory=list
    )

    javascript_files: list[str] = field(
        default_factory=list
    )

    evidence: list[Evidence] = field(
        default_factory=list
    )

    findings: list[Finding] = field(
        default_factory=list
    )

    validation_results: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    last_validation: dict[str, Any] | None = None

    def add_validation_result(
        self,
        vulnerability: str,
        status: str,
        details: dict[str, Any] | None = None,
    ):
        result = {
            "vulnerability": vulnerability,
            "status": status,
            "details": details or {},
        }

        self.validation_results[vulnerability] = result
        self.last_validation = result

    def is_vulnerability_confirmed(
        self,
        vulnerability: str,
    ) -> bool:

        result = self.validation_results.get(
            vulnerability
        )

        if not result:
            return False

        return result.get("status") == "confirmed"

    def add_evidence(
        self,
        evidence_type: str,
        description: str,
        data: dict[str, Any] | None = None,
    ):
        self.evidence.append(
            Evidence(
                type=evidence_type,
                description=description,
                data=data or {},
            )
        )

    def add_finding(
        self,
        title: str,
        severity: str,
        confidence: str,
        endpoint: str | None = None,
        description: str = "",
        evidence: list[str] | None = None,
        remediation: str = "",
    ):
        self.findings.append(
            Finding(
                title=title,
                severity=severity,
                confidence=confidence,
                endpoint=endpoint,
                description=description,
                evidence=evidence or [],
                remediation=remediation,
            )
        )