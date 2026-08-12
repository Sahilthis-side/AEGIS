from pathlib import Path

from aegis.core.context import ScanContext


def generate_markdown_report(
    context: ScanContext,
    output_path: str = "aegis-report.md",
):
    lines = []

    lines.append("# Aegis Security Report")
    lines.append("")

    lines.append("## Target")
    lines.append("")

    lines.append(
        f"- **Path:** `{context.target_path}`"
    )

    if context.base_url:
        lines.append(
            f"- **URL:** `{context.base_url}`"
        )

    lines.append(
        f"- **Language:** {context.language}"
    )

    lines.append(
        f"- **Framework:** {context.framework}"
    )

    lines.append("")

    # ==========================================
    # Attack Surface
    # ==========================================

    lines.append("## Attack Surface")
    lines.append("")

    lines.append(
        f"- Technologies: "
        f"{', '.join(context.technologies) or 'None'}"
    )

    lines.append(
        f"- Endpoints: {len(context.endpoints)}"
    )

    lines.append(
        f"- Links: {len(context.links)}"
    )

    lines.append("")

    # ==========================================
    # Findings
    # ==========================================

    lines.append("## Findings")
    lines.append("")

    if not context.findings:

        lines.append(
            "No confirmed vulnerabilities were found."
        )

    for index, finding in enumerate(
        context.findings,
        start=1,
    ):

        lines.append(
            f"### {index}. {finding.title}"
        )

        lines.append("")

        lines.append(
            f"- **Severity:** {finding.severity}"
        )

        lines.append(
            f"- **Confidence:** {finding.confidence}"
        )

        if finding.endpoint:

            lines.append(
                f"- **Endpoint:** "
                f"`{finding.endpoint}`"
            )

        lines.append("")

        if finding.description:

            lines.append(
                f"**Description**\n\n"
                f"{finding.description}"
            )

            lines.append("")

        if finding.evidence:

            lines.append("**Evidence**")
            lines.append("")

            for evidence in finding.evidence:

                lines.append(
                    f"- {evidence}"
                )

            lines.append("")

        if finding.remediation:

            lines.append(
                "**Remediation**"
            )

            lines.append("")

            lines.append(
                finding.remediation
            )

            lines.append("")

    # ==========================================
    # Evidence
    # ==========================================

    lines.append("## Evidence Records")
    lines.append("")

    lines.append(
        f"Total evidence records: "
        f"{len(context.evidence)}"
    )

    lines.append("")

    path = Path(output_path)

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return path