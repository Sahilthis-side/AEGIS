from aegis.agents.model import AgentModel
from aegis.core.context import ScanContext
from aegis.tools.registry import ToolRegistry


class SecurityAgent:

    def __init__(
        self,
        model: AgentModel,
        tools: ToolRegistry,
        context: ScanContext,
        attack_surface: list[dict] | None = None,
    ):
        self.model = model
        self.tools = tools
        self.context = context
        self.attack_surface = attack_surface or []

    def build_context(self):

        return {
            "last_tool_result": getattr(
                self,
                "last_tool_result",
                None,
            ),

            "target_path": self.context.target_path,
            "base_url": self.context.base_url,

            "language": self.context.language,
            "framework": self.context.framework,

            "technologies": (
                self.context.technologies
            ),

            "endpoints": (
                self.context.endpoints
            ),

            "links": (
                self.context.links
            ),

            "javascript_files": (
                self.context.javascript_files
            ),
            "attack_surface": self.attack_surface,

            "findings": [
                {
                    "title": finding.title,
                    "severity": finding.severity,
                    "confidence": finding.confidence,
                    "endpoint": finding.endpoint,
                }
                for finding in self.context.findings
            ],
        }

    def run(self, max_steps: int = 10):

        for step in range(max_steps):

            print(
                f"\n[Agent] Step {step + 1}"
            )

            model_context = self.build_context()

            response = self.model.think(
                context=model_context,
                tools=self.tools.schemas(),
            )

            print(
                f"[Agent] {response.message}"
            )

            if response.finished:

                print(
                    "[Agent] Investigation finished."
                )

                return

            if not response.tool_name:

                print(
                    "[Agent] No tool selected."
                )

                return

            print(
                f"[Agent] Tool: "
                f"{response.tool_name}"
            )

            print(
                f"[Agent] Arguments: "
                f"{response.tool_arguments}"
            )

            result = self.tools.execute(
                response.tool_name,
                **(
                    response.tool_arguments
                    or {}
                ),
            )

            if result.success:

                print(
                    "[Tool] Success"
                )

                self.last_tool_result = (
                    result.output
                )

                self.context.add_evidence(
                    evidence_type="tool_result",
                    description=(
                        f"Tool '{response.tool_name}' "
                        f"executed successfully."
                    ),
                    data={
                        "tool": response.tool_name,
                        "arguments": (
                            response.tool_arguments
                        ),
                        "result": result.output,
                    },
                )

                self.model.observe_tool_result(
                    response,
                    result.output,
                )

            else:

                print(
                    f"[Tool] Failed: "
                    f"{result.error}"
                )

                self.last_tool_result = {
                    "error": result.error
                }

                self.model.observe_tool_result(
                    response,
                    {
                        "error": result.error
                    },
                )