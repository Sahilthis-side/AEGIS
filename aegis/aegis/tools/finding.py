from aegis.core.context import ScanContext
from aegis.tools.base import Tool, ToolResult


class CreateFindingTool(Tool):

    name = "create_finding"

    description = (
        "Create a security finding after Aegis "
        "has confirmed the vulnerability."
    )

    def __init__(self, context: ScanContext):
        self.context = context

    def execute(
        self,
        title: str,
        severity: str,
        confidence: str,
        endpoint: str | None = None,
        description: str = "",
        evidence: list[str] | None = None,
        remediation: str = "",
        vulnerability: str | None = None,
    ) -> ToolResult:

        validation = self.context.last_validation

        if validation is None:
            return ToolResult(
                success=False,
                output=None,
                error=(
                    "Finding rejected: no security "
                    "validation has been performed."
                ),
            )

        validated_vulnerability = (
            validation.get("vulnerability")
        )

        validation_status = (
            validation.get("status")
        )

        if (
            vulnerability is not None
            and vulnerability != validated_vulnerability
        ):
            return ToolResult(
                success=False,
                output=None,
                error=(
                    "Finding rejected: requested "
                    f"vulnerability '{vulnerability}' "
                    "does not match the vulnerability "
                    f"validated by Aegis "
                    f"('{validated_vulnerability}')."
                ),
            )

        if validation_status != "confirmed":
            return ToolResult(
                success=False,
                output=None,
                error=(
                    "Finding rejected: Aegis validator "
                    f"status for '{validated_vulnerability}' "
                    f"is '{validation_status}'. "
                    "Only confirmed vulnerabilities "
                    "can become findings."
                ),
            )

        self.context.add_finding(
            title=title,
            severity=severity,
            confidence=confidence,
            endpoint=endpoint,
            description=description,
            evidence=evidence or [],
            remediation=remediation,
        )

        return ToolResult(
            success=True,
            output={
                "finding_created": True,
                "title": title,
                "vulnerability": validated_vulnerability,
                "validation_status": validation_status,
            },
        )