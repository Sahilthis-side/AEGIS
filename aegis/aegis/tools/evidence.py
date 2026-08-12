from aegis.core.context import ScanContext
from aegis.tools.base import Tool, ToolResult


import json


class RecordEvidenceTool(Tool):

    name = "record_evidence"

    description = (
        "Record concrete security evidence collected "
        "during the investigation."
    )

    def __init__(self, context):
        self.context = context

    def execute(
        self,
        evidence_type: str,
        data=None,
        description: str = "",
    ) -> ToolResult:

        # Make the tool tolerant if the model omits
        # the description.
        if not description:
            description = (
                f"Evidence collected for "
                f"{evidence_type}."
            )

        # The model sometimes returns JSON as a string.
        # Convert it back into a Python object.
        if isinstance(data, str):

            try:
                data = json.loads(data)

            except json.JSONDecodeError:

                data = {
                    "raw": data
                }

        if data is None:
            data = {}

        self.context.add_evidence(
            evidence_type=evidence_type,
            description=description,
            data=data,
        )

        return ToolResult(
            success=True,
            output={
                "recorded": True,
                "evidence_type": evidence_type,
                "description": description,
            },
        )
