import json
import os

from anthropic import Anthropic

from aegis.agents.model import (
    AgentModel,
    AgentResponse,
)


SYSTEM_PROMPT = """
You are Aegis, an autonomous application security
testing agent.

You investigate applications running inside an
authorized sandbox.

Your responsibilities are:

1. Understand the application's attack surface.
2. Form security hypotheses.
3. Investigate using the available tools.
4. Validate vulnerabilities with evidence.
5. Never report a vulnerability as confirmed
   without sufficient evidence.
"""


class AnthropicProvider(AgentModel):

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
    ):

        self.client = Anthropic(
            api_key=(
                api_key
                or os.getenv("ANTHROPIC_API_KEY")
            )
        )

        self.model = model

    def think(
        self,
        context,
        tools,
    ):

        prompt = json.dumps(
            context,
            indent=2,
            default=str,
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Current scan state:\n\n"
                        + prompt
                        + "\n\n"
                        "Choose the next action."
                    ),
                }
            ],
        )

        text = ""

        for block in response.content:

            if getattr(
                block,
                "type",
                None
            ) == "text":

                text += block.text

        return AgentResponse(
            message=text,
            finished=True,
        )