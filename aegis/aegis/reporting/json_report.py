import json
from dataclasses import asdict
from pathlib import Path

from aegis.core.context import ScanContext


def generate_json_report(
    context: ScanContext,
    output_path: str = "aegis-report.json",
):
    report = {
        "target": {
            "path": context.target_path,
            "base_url": context.base_url,
            "language": context.language,
            "framework": context.framework,
            "package_manager": context.package_manager,
        },

        "attack_surface": {
            "technologies": context.technologies,
            "endpoints": context.endpoints,
            "links": context.links,
            "javascript_files": (
                context.javascript_files
            ),
        },

        "findings": [
            asdict(finding)
            for finding in context.findings
        ],

        "evidence": [
            asdict(evidence)
            for evidence in context.evidence
        ],
    }

    path = Path(output_path)

    path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path