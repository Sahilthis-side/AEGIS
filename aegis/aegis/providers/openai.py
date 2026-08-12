import json

from openai import OpenAI

from aegis.agents.model import (
    AgentModel,
    AgentResponse,
)
from aegis.config.settings import settings


SYSTEM_PROMPT = """
You are Aegis, an autonomous application security
testing agent.

You are testing an application that has been
explicitly authorized by the user.

Your responsibilities:

1. Understand the application's attack surface.
2. Form security hypotheses.
3. Investigate using available tools.
4. Validate vulnerabilities with evidence.
5. Never declare a vulnerability confirmed without
   sufficient evidence.
6. Prefer deterministic validation tools.
7. Use the sandbox for application interaction.
8. Do not invent evidence.
"""


class OpenAIProvider(AgentModel):

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ):

        key = (
            api_key
            or settings.openai_api_key
        )

        if not key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=key
        )

        self.model = (
            model
            or settings.openai_model
        )

    def think(
        self,
        context,
        tools,
    ):

        response = self.client.responses.create(
            model=self.model,

            instructions=SYSTEM_PROMPT,

            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Current Aegis scan state:\n\n"
                                + json.dumps(
                                    context,
                                    indent=2,
                                    default=str,
                                )
                            ),
                        }
                    ],
                }
            ],

            tools=tools,
        )
        for item in response.output:

            if item.type == "function_call":

                return AgentResponse(
                    message=(
                        response.output_text
                        or "Selecting a security tool."
                    ),

                    tool_name=item.name,

                    tool_arguments=json.loads(
                        item.arguments
                    ),

                    finished=False,

                    provider_data={
                        "call_id": item.call_id,
                    },
                )
        return AgentResponse(
            message=response.output_text,
            finished=True,
        )