from google import genai
from google.genai import types

import json

from aegis.agents.model import (
    AgentModel,
    AgentResponse,
)

from aegis.config.settings import settings

SYSTEM_PROMPT = """
You are the security analysis agent inside Aegis.

Aegis is a developer security testing tool. The user
has explicitly provided the application being tested
and authorized Aegis to perform security testing.

IMPORTANT SAFETY BOUNDARY:

- Only interact with the application through tools
  provided by Aegis.
- The application is running inside an isolated
  local sandbox.
- Do not target unrelated systems.
- Do not perform actions outside the supplied target.
- Do not invent targets, credentials, or evidence.

Your job is to investigate the authorized sandbox
application for security vulnerabilities.

You should:

1. Analyze the available attack surface.
2. Identify potentially dangerous inputs and behavior.
3. Form testable security hypotheses.
4. Select appropriate Aegis tools to investigate them.
5. Prefer deterministic validators whenever available.
6. Compare observations and collect evidence.
7. Only create a finding when the evidence supports
   the vulnerability.
8. Clearly distinguish hypotheses from confirmed findings.

For example, if reconnaissance discovers:

GET /search
parameter: q

you may investigate whether the q parameter produces
SQL injection behavior by using the Aegis validation
tools.

Do not merely describe how a vulnerability could exist.
Use the available Aegis tools to obtain evidence.

The application is intentionally provided to Aegis for
authorized security testing.
"""



class GeminiProvider(AgentModel):

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ):

        key = (
            api_key
            or settings.gemini_api_key
        )

        if not key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=key
        )

        self.model = (
            model
            or settings.gemini_model
        )

        self.contents = []

    def _build_tools(self, tools):
        """
        Convert Aegis tool schemas into Gemini
        function declarations.
        """

        declarations = []

        for tool in tools:

            declaration = {
                key: value
                for key, value in tool.items()
                if key != "type"
            }

            declarations.append(
                declaration
            )

        return [
            types.Tool(
                function_declarations=declarations
            )
        ]

    def think(
        self,
        context,
        tools,
    ):
        if not self.contents:

            prompt = (
                SYSTEM_PROMPT
                + "\n\nCurrent Aegis scan state:\n\n"
                + json.dumps(
                    context,
                    indent=2,
                    default=str,
                )
                + "\n\n"
                "Begin investigating the target. "
                "Choose the most useful next tool."
            )

            self.contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text=prompt
                        )
                    ],
                )
            )
        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=self.contents,
                config=types.GenerateContentConfig(
                    tools=self._build_tools(tools)
                ),
            )
        )

        candidate = response.candidates[0]

        model_content = candidate.content
        for part in model_content.parts:

            function_call = (
                getattr(
                    part,
                    "function_call",
                    None
                )
            )

            if function_call:

                arguments = dict(
                    function_call.args or {}
                )

                self.contents.append(
                    model_content
                )

                return AgentResponse(
                    message=(
                        response.text
                        or (
                            f"Gemini selected "
                            f"{function_call.name}."
                        )
                    ),

                    tool_name=(
                        function_call.name
                    ),

                    tool_arguments=arguments,

                    finished=False,

                    provider_data={
                        "function_name": (
                            function_call.name
                        ),
                        "function_id": getattr(
                            function_call,
                            "id",
                            None,
                        ),
                    },
                )
        self.contents.append(
            model_content
        )

        return AgentResponse(
            message=response.text or "",
            finished=True,
        )

    def observe_tool_result(
        self,
        response: AgentResponse,
        result,
    ):
        """
        Send the tool result back to Gemini.
        """

        function_name = (
            response.provider_data[
                "function_name"
            ]
        )

        function_id = (
            response.provider_data.get(
                "function_id"
            )
        )

        function_response = (
            types.Part.from_function_response(
                name=function_name,
                response={
                    "result": result
                },
                id=function_id,
            )
        )

        self.contents.append(
            types.Content(
                role="user",
                parts=[
                    function_response
                ],
            )
        )
