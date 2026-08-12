from pathlib import Path
from dataclasses import dataclass
import json


@dataclass
class TargetInfo:
    path: str
    language: str
    framework: str
    package_manager: str
    start_command: str | None


def detect_target(target_path: str) -> TargetInfo:
    path = Path(target_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Target does not exist: {path}")
    package_json = path / "package.json"

    if package_json.exists():
        with open(package_json, "r", encoding="utf-8") as f:
            package = json.load(f)

        dependencies = {
            **package.get("dependencies", {}),
            **package.get("devDependencies", {}),
        }

        framework = "Node.js"

        if "next" in dependencies:
            framework = "Next.js"
        elif "express" in dependencies:
            framework = "Express"
        elif "fastify" in dependencies:
            framework = "Fastify"
        elif "react" in dependencies:
            framework = "React"

        scripts = package.get("scripts", {})

        start_command = None

        if "dev" in scripts:
            start_command = "npm run dev"
        elif "start" in scripts:
            start_command = "npm start"

        return TargetInfo(
            path=str(path),
            language="JavaScript/TypeScript",
            framework=framework,
            package_manager="npm",
            start_command=start_command,
        )
    if (path / "requirements.txt").exists():
        return TargetInfo(
            path=str(path),
            language="Python",
            framework="Python",
            package_manager="pip",
            start_command=None,
        )

    if (path / "pyproject.toml").exists():
        return TargetInfo(
            path=str(path),
            language="Python",
            framework="Python",
            package_manager="pip",
            start_command=None,
        )
    if (path / "pom.xml").exists():
        return TargetInfo(
            path=str(path),
            language="Java",
            framework="Maven",
            package_manager="maven",
            start_command=None,
        )
    if (path / "go.mod").exists():
        return TargetInfo(
            path=str(path),
            language="Go",
            framework="Go",
            package_manager="go",
            start_command=None,
        )

    return TargetInfo(
        path=str(path),
        language="Unknown",
        framework="Unknown",
        package_manager="Unknown",
        start_command=None,
    )
