from pathlib import Path
from dataclasses import dataclass
import json
import xml.etree.ElementTree as ET

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
        raise FileNotFoundError(
            f"Target does not exist: {path}"
        )

    # ==========================================
    # JAVASCRIPT / TYPESCRIPT
    # ==========================================

    package_json = path / "package.json"

    if package_json.exists():

        with open(
            package_json,
            "r",
            encoding="utf-8",
        ) as file:

            package = json.load(file)

        dependencies = {
            **package.get(
                "dependencies",
                {},
            ),
            **package.get(
                "devDependencies",
                {},
            ),
        }

        framework = "Node.js"

        if "next" in dependencies:
            framework = "Next.js"

        elif "express" in dependencies:
            framework = "Express"

        elif "fastify" in dependencies:
            framework = "Fastify"

        elif "koa" in dependencies:
            framework = "Koa"

        elif "hapi" in dependencies:
            framework = "Hapi"

        elif "react" in dependencies:
            framework = "React"

        elif "vue" in dependencies:
            framework = "Vue"

        scripts = package.get(
            "scripts",
            {},
        )

        start_command = None

        if "dev" in scripts:
            start_command = "npm run dev"

        elif "start" in scripts:
            start_command = "npm start"

        elif "serve" in scripts:
            start_command = "npm run serve"

        return TargetInfo(
            path=str(path),
            language="JavaScript/TypeScript",
            framework=framework,
            package_manager="npm",
            start_command=start_command,
        )

    # ==========================================
    # PYTHON
    # ==========================================

    requirements = path / "requirements.txt"
    pyproject = path / "pyproject.toml"

    if requirements.exists() or pyproject.exists():

        framework = "Python"
        start_command = None

        # --------------------------------------
        # Detect dependencies
        # --------------------------------------

        dependencies_text = ""

        if requirements.exists():

            dependencies_text = (
                requirements
                .read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                .lower()
            )

        if pyproject.exists():

            dependencies_text += (
                pyproject
                .read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                .lower()
            )

        # --------------------------------------
        # FastAPI
        # --------------------------------------

        if "fastapi" in dependencies_text:

            framework = "FastAPI"

            if (path / "main.py").exists():

                start_command = (
                    "uvicorn main:app "
                    "--host 0.0.0.0 "
                    "--port 3000"
                )

        # --------------------------------------
        # Flask
        # --------------------------------------

        elif "flask" in dependencies_text:

            framework = "Flask"

            if (path / "app.py").exists():

                start_command = (
                    "flask --app app "
                    "run --host 0.0.0.0 "
                    "--port 3000"
                )

            elif (path / "main.py").exists():

                start_command = (
                    "flask --app main "
                    "run --host 0.0.0.0 "
                    "--port 3000"
                )

        # --------------------------------------
        # Django
        # --------------------------------------

        elif "django" in dependencies_text:

            framework = "Django"

            if (path / "manage.py").exists():

                start_command = (
                    "python manage.py "
                    "runserver 0.0.0.0:3000"
                )

        # --------------------------------------
        # Generic Python
        # --------------------------------------

        else:

            framework = "Python"

            if (path / "main.py").exists():

                start_command = (
                    "python main.py"
                )

            elif (path / "app.py").exists():

                start_command = (
                    "python app.py"
                )

        return TargetInfo(
            path=str(path),
            language="Python",
            framework=framework,
            package_manager="pip",
            start_command=start_command,
        )

    # ==========================================
    # JAVA / MAVEN
    # ==========================================

    pom_xml = path / "pom.xml"

    if (path / "pom.xml").exists():

        framework = "Maven"
        start_command = "mvn spring-boot:run -Dspring-boot.run.arguments=\"--server.port=3000\""

        try:
            tree = ET.parse(path / "pom.xml")
            root = tree.getroot()

            namespaces = {
                "m": "http://maven.apache.org/POM/4.0.0"
            }

            pom_text = ET.tostring(
                root,
                encoding="unicode"
            ).lower()

            if (
                "spring-boot" in pom_text
                or "springframework" in pom_text
            ):
                framework = "Spring Boot"

        except ET.ParseError:
            pass

        return TargetInfo(
            path=str(path),
            language="Java",
            framework=framework,
            package_manager="maven",
            start_command=start_command,
        )

    # ==========================================
    # JAVA / GRADLE
    # ==========================================

    if (
        (path / "build.gradle").exists()
        or
        (path / "build.gradle.kts").exists()
    ):

        build_file = (
            path / "build.gradle"
        )

        if not build_file.exists():

            build_file = (
                path / "build.gradle.kts"
            )

        build_text = (
            build_file
            .read_text(
                encoding="utf-8",
                errors="ignore",
            )
            .lower()
        )

        framework = "Gradle"

        if "spring-boot" in build_text:

            framework = "Spring Boot"

            start_command = (
                "./gradlew bootRun "
                "-Dserver.port=3000"
            )

        else:

            start_command = (
                "./gradlew bootRun "
                "-Dserver.port=3000"
            )

        return TargetInfo(
            path=str(path),
            language="Java",
            framework=framework,
            package_manager="gradle",
            start_command=start_command,
        )

    # ==========================================
    # GO
    # ==========================================

    if (path / "go.mod").exists():

        return TargetInfo(
            path=str(path),
            language="Go",
            framework="Go",
            package_manager="go",
            start_command=(
                "go run ."
            ),
        )

    # ==========================================
    # UNKNOWN
    # ==========================================

    return TargetInfo(
        path=str(path),
        language="Unknown",
        framework="Unknown",
        package_manager="Unknown",
        start_command=None,
    )