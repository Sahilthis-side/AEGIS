from aegis.core.context import ScanContext
from aegis.tools.base import Tool, ToolResult

from aegis.security.engine import VulnerabilityEngine


class SecurityTestTool(Tool):

    name = "security_test"

    description = (
        "Run a deterministic security validator "
        "against the authorized sandbox application."
    )

    def __init__(
        self,
        engine: VulnerabilityEngine,
        context: ScanContext,
    ):
        self.engine = engine
        self.context = context

    def execute(
        self,
        vulnerability: str,
        **kwargs,
    ) -> ToolResult:

        result = self.engine.test(
            vulnerability,
            **kwargs,
        )

        self.context.add_validation_result(
            vulnerability=result.vulnerability,
            status=result.status,
            details=result.details,
        )

        return ToolResult(
            success=True,
            output={
                "vulnerability": result.vulnerability,
                "status": result.status,
                "confidence": result.confidence,
                "title": result.title,
                "description": result.description,
                "evidence": result.evidence,
                "details": result.details,
                "remediation": result.remediation,
            },
        )
