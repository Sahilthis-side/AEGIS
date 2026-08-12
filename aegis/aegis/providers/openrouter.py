import json
import re
from json_repair import repair_json
from openai import OpenAI

from aegis.agents.model import (
    AgentModel,
    AgentResponse,
)

from aegis.config.settings import settings


SYSTEM_PROMPT = """
You are Aegis, an autonomous application security
testing agent.

The user has explicitly authorized Aegis to test the
application supplied to the scanner.

The application is running inside an isolated sandbox.

Only interact with the supplied target through Aegis
tools.

Your job is to:

1. Understand the application's attack surface.
2. Identify potentially vulnerable inputs.
3. Form testable security hypotheses.
4. Select appropriate Aegis tools.
5. Analyze tool results.
6. Use deterministic validators whenever possible.
7. Collect concrete evidence.
8. Only create a finding when evidence supports it.

Do not invent evidence.

A hypothesis is not a confirmed vulnerability.

Use the available tools to investigate the target.
For HTTP requests, always provide the endpoint path and query parameters separately. Use: { "method": "GET", "path": "/search", "params": { "q": "value" } } Do not manually construct or URL-encode the query string inside the path.
IMPORTANT VALIDATION RULE: If a deterministic validator reports that a vulnerability is confirmed, do not perform additional unnecessary attack attempts. Instead: 1. Review the validator evidence. 2. Record the confirmed finding. 3. Stop the investigation for that vulnerability. If a validator does not confirm the hypothesis, continue investigating using appropriate tools.
SOURCE CODE ANALYSIS:

When an endpoint accepts user-controlled input,
inspect the relevant source code when possible.

Use read_source to determine:

- where the input enters the application,
- how the input is transformed,
- whether it reaches a sensitive operation,
- whether parameterization or validation is present,
- and the likely root cause of a vulnerability.

Do not claim that source code proves exploitability
by itself. Runtime validation and concrete evidence
should be used to confirm vulnerabilities.

When creating a finding, include the relevant source
file and line numbers in the evidence when available.
SOURCE FILE WORKFLOW:

When source-code analysis is useful but the filename
is unknown:

1. Call list_source_files.
2. Identify the source file relevant to the endpoint.
3. Call read_source with the actual filename.
4. Use the source code to understand the root cause.

Never guess filenames such as index.js or app.js when
the available source files have not been inspected.
VULNERABILITY TESTING:

Aegis provides a security_test tool backed by
deterministic vulnerability validators.

You may investigate these vulnerability classes:

- sql_injection
- xss
- ssrf
- idor
- path_traversal
- command_injection
- authentication_bypass

Do not claim that a vulnerability exists merely
because an endpoint looks suspicious.

Use security_test to obtain deterministic evidence.

The validator result has three possible states:

confirmed:
    Sufficient evidence exists.

not_confirmed:
    The test completed but the vulnerability
    was not demonstrated.

insufficient_evidence:
    The validator could not safely establish
    whether the vulnerability exists.

Only create a confirmed finding when the
validator or other concrete evidence supports it.

Do not invent validator results.
When SQL injection is suspected, use:

security_test(
    vulnerability="sql_injection",
    path="/search",
    parameter="q"
)

Do not call validate_sqli directly. The vulnerability
engine is responsible for selecting the validator.
EVIDENCE RULES:

After security_test returns a result:

1. If status == "confirmed":
   Record the evidence.
   Then create a finding.

2. If status == "not_confirmed":
   Record the test result if useful.
   Do not create a vulnerability finding.

3. If status == "insufficient_evidence":
   Do not create a confirmed finding.
   You may investigate further using available tools.

When calling record_evidence, ALWAYS provide:
- evidence_type
- description
- data

The description must explain what the evidence demonstrates.

Never claim confirmation without concrete evidence.
XSS VALIDATION RULE:

Do not declare XSS confirmed merely because
a payload is reflected in an HTTP response.

Reflection is evidence of a potential XSS issue.

A confirmed XSS finding requires evidence that
the injected content can execute in the relevant
browser context.

Until browser execution validation exists,
classify reflection-only results as
insufficient_evidence.
FINDING CREATION RULE:

create_finding is protected by an Aegis validation gate.

Before creating a finding, you MUST have a
security_test result with:

status = "confirmed"

If security_test returns:

- confirmed:
  You may create a finding.

- not_confirmed:
  Do not create a finding.

- insufficient_evidence:
  Do not create a finding.

Source-code analysis, payload reflection, or your
own reasoning cannot override the validator status.

If a validator returns insufficient_evidence,
continue investigating only if another available
tool can provide stronger evidence.
"""
def parse_tool_arguments(raw_arguments: str) -> dict:
    """
    Parse JSON generated by an LLM.

    Free models can occasionally return malformed or
    incomplete JSON. Repair common formatting problems
    before giving the arguments to the tool registry.
    """

    if not raw_arguments:
        raise ValueError(
            "Model returned empty tool arguments."
        )

    try:
        return json.loads(raw_arguments)

    except json.JSONDecodeError:

        try:
            repaired = repair_json(
                raw_arguments
            )

            parsed = json.loads(repaired)

            if not isinstance(parsed, dict):
                raise ValueError(
                    "Tool arguments must be a JSON object."
                )

            return parsed

        except Exception as error:

            raise ValueError(
                "Model returned invalid tool arguments: "
                f"{raw_arguments}"
            ) from error
class OpenRouterProvider(AgentModel):

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ):

        key = (
            api_key
            or settings.openrouter_api_key
        )

        if not key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=key,
            base_url=settings.openrouter_base_url,
        )

        self.model = (
            model
            or settings.openrouter_model
        )

        self.messages = []

    def think(
        self,
        context,
        tools,
    ):

        # ----------------------------------------
        # First model request
        # ----------------------------------------

        if not self.messages:

            self.messages.append(
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            )

        # ----------------------------------------
        # Add current scan state
        # ----------------------------------------

        self.messages.append(
            {
                "role": "user",
                "content": (
                    "Current Aegis scan state:\n\n"
                    + json.dumps(
                        context,
                        indent=2,
                        default=str,
                    )
                ),
            }
        )

        # ----------------------------------------
        # Ask OpenRouter
        # ----------------------------------------

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
            )
        )

        message = (
            response.choices[0].message
        )

        # ----------------------------------------
        # Preserve assistant response
        # ----------------------------------------

        assistant_message = {
            "role": "assistant",
            "content": message.content,
        }

        if message.tool_calls:

            normalized_tool_calls = []

            for call in message.tool_calls:

                raw_arguments = (
                    call.function.arguments
                    or "{}"
                )

                # Normalize / repair model-generated arguments
                parsed_arguments = parse_tool_arguments(
                    raw_arguments
                )

                normalized_tool_calls.append(
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": json.dumps(
                                parsed_arguments,
                                separators=(",", ":"),
                            ),
                        },
                    }
                )

            assistant_message[
                "tool_calls"
            ] = normalized_tool_calls

        self.messages.append(
            assistant_message
        )

        # ----------------------------------------
        # Tool call
        # ----------------------------------------

        if message.tool_calls:

            call = message.tool_calls[0]

            return AgentResponse(
                message=(
                    message.content
                    or (
                        f"Selected tool "
                        f"{call.function.name}."
                    )
                ),

                tool_name=(
                    call.function.name
                ),

                tool_arguments=parse_tool_arguments(
                    call.function.arguments
                ),

                finished=False,

                provider_data={
                    "tool_call_id": call.id,
                },
            )

        # ----------------------------------------
        # No tool call
        # ----------------------------------------

        return AgentResponse(
            message=message.content or "",
            finished=True,
        )

    def observe_tool_result(
        self,
        response: AgentResponse,
        result,
    ):

        tool_call_id = (
            response.provider_data[
                "tool_call_id"
            ]
        )

        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(
                    result,
                    default=str,
                ),
            }
        )
