import time

import typer
from rich.console import Console
from rich.table import Table

from aegis.core.detector import detect_target
from aegis.core.recon import ReconEngine
from aegis.sandbox.docker import DockerSandbox
from aegis.core.context import ScanContext
from aegis.agents.agent import SecurityAgent
from aegis.providers.openai import OpenAIProvider
from aegis.providers.openrouter import (
    OpenRouterProvider,
)
from aegis.tools.evidence import RecordEvidenceTool
from aegis.tools.finding import CreateFindingTool
from aegis.tools.http import HTTPRequestTool
from aegis.tools.registry import ToolRegistry
from aegis.tools.sqli import SQLInjectionValidator
from aegis.reporting.json_report import generate_json_report
from aegis.reporting.markdown import generate_markdown_report
from aegis.tools.source import ReadSourceTool
from aegis.tools.files import ListSourceFilesTool
from aegis.security.path_traversal import (
    PathTraversalSecurityValidator,
)
from aegis.security.engine import (
    VulnerabilityEngine,
)
from aegis.security.sqli import (
    SQLInjectionSecurityValidator,
)
from aegis.tools.security import (
    SecurityTestTool,
)
from aegis.security.xss import (
    XSSSecurityValidator,
)
from aegis.security.attack_surface import (
    AttackSurfaceAnalyzer,
)
from aegis.security.ssrf import (
    SSRFSecurityValidator,
)
app = typer.Typer(
    name="aegis",
    help="AI-powered autonomous application security scanner."
)

console = Console()


@app.command()
def scan(target: str):
    """Scan a local application or target."""

    console.print(
        "\n[bold cyan]╔══════════════════════════════════╗[/bold cyan]"
    )
    console.print(
        "[bold cyan]║       AEGIS SECURITY SCANNER     ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]╚══════════════════════════════════╝[/bold cyan]\n"
    )

    console.print(f"[bold]Target:[/bold] {target}\n")

    # ==========================================
    # TARGET DETECTION
    # ==========================================

    try:
        info = detect_target(target)

    except FileNotFoundError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(code=1)

    console.print("[green]✓[/green] Target detected\n")
    context = ScanContext(target_path=info.path,language=info.language,framework=info.framework,package_manager=info.package_manager,)


    table = Table(title="Target Information")

    table.add_column("Property")
    table.add_column("Value")

    table.add_row("Path", info.path)
    table.add_row("Language", info.language)
    table.add_row("Framework", info.framework)
    table.add_row("Package Manager", info.package_manager)
    table.add_row(
        "Start Command",
        info.start_command or "Unknown"
    )

    console.print(table)

    # ==========================================
    # DOCKER SANDBOX
    # ==========================================

    console.print("\n[bold cyan]Sandbox[/bold cyan]")

    sandbox = DockerSandbox(info.path)

    try:

        sandbox.start()

        console.print(
            "[green]✓[/green] Sandbox created"
        )

        # Install dependencies
        sandbox.install_dependencies()

        # Start application
        sandbox.start_application()

        # Wait for application
        sandbox.wait_for_health()

        base_url = (
            f"http://127.0.0.1:{sandbox.host_port}"
        )
        context.base_url = base_url

        console.print(
            "\n[bold green]✓ TARGET READY[/bold green]"
        )

        console.print(
            f"Application: [cyan]{base_url}[/cyan]"
        )

        # ==========================================
        # RECONNAISSANCE
        # ==========================================

        console.print(
            "\n[bold cyan]Reconnaissance[/bold cyan]"
        )

        recon = ReconEngine(base_url)

        result = recon.run()
        context.technologies = result.technologies

        context.links = result.links

        context.javascript_files = (
            result.javascript_files
        )

        context.endpoints = [
            {
                "path": endpoint.path,
                "method": endpoint.method,
                "status_code": endpoint.status_code,
                "content_type": endpoint.content_type,
                "parameters": [
                    {
                        "name": parameter.name,
                        "location": parameter.location,
                        "value": parameter.value,
                    }
                    for parameter in endpoint.parameters
                ],
            }
            for endpoint in result.endpoints
        ]
        if not result.reachable:
            context.add_evidence(
                evidence_type="recon",
                description="Target successfully reached.",
                data={
                    "base_url": base_url,
                    "server": result.server,
                    "technologies": result.technologies,
                },
            )
            console.print(
                "[red]✗ Target is not reachable[/red]"
            )

            raise typer.Exit(code=1)

        console.print(
            "[green]✓[/green] Target is reachable"
        )

        # Server
        if result.server:

            console.print(
                f"[green]✓[/green] Server: "
                f"{result.server}"
            )

        # Technologies
        if result.technologies:

            console.print(
                "[green]✓[/green] Technologies: "
                + ", ".join(result.technologies)
            )

        # ==========================================
        # ENDPOINTS
        # ==========================================

        if result.endpoints:

            console.print(
                "\n[bold]Discovered Endpoints[/bold]"
            )

            endpoint_table = Table()

            endpoint_table.add_column("Method")
            endpoint_table.add_column("Path")
            endpoint_table.add_column("Status")
            endpoint_table.add_column("Parameters")

            for endpoint in result.endpoints:

                parameters = ", ".join(
                    parameter.name
                    for parameter in endpoint.parameters
                )

                endpoint_table.add_row(
                    endpoint.method,
                    endpoint.path,
                    str(
                        endpoint.status_code
                        if endpoint.status_code is not None
                        else "-"
                    ),
                    parameters or "-"
                )

            console.print(endpoint_table)

        # ==========================================
        # LINKS
        # ==========================================

        if result.links:

            console.print(
                "\n[bold]Discovered Links[/bold]"
            )

            for link in result.links:

                console.print(
                    f"  • {link}"
                )

        # ==========================================
        # JAVASCRIPT
        # ==========================================

        if result.javascript_files:

            console.print(
                "\n[bold]JavaScript Files[/bold]"
            )

            for js_file in result.javascript_files:

                console.print(
                    f"  • {js_file}"
                )

        console.print(
            "\n[bold green]✓ Reconnaissance completed[/bold green]"
        )
        console.print(
            f"\n[bold]Scan Context[/bold]"
        )

        console.print(
            f"  Target: {context.target_path}"
        )

        console.print(
            f"  Framework: {context.framework}"
        )

        console.print(
            f"  Endpoints: {len(context.endpoints)}"
        )

        console.print(
            f"  Links: {len(context.links)}"
        )

        console.print(
            f"  JavaScript files: "
            f"{len(context.javascript_files)}"
        )

        console.print(
            f"  Evidence records: "
            f"{len(context.evidence)}"
        )

        console.print(
            f"  Findings: "
            f"{len(context.findings)}"
        )
        # ==========================================
        # SECURITY AGENT
        # ==========================================

        console.print(
            "\n[bold cyan]Security Agent[/bold cyan]"
        )

        tools = ToolRegistry()

        tools.register(
            HTTPRequestTool(base_url)
        )

        security_engine = VulnerabilityEngine()

        security_engine.register(
            SQLInjectionSecurityValidator(
                base_url
            )
        )
        security_engine.register(
            XSSSecurityValidator(
                base_url
            )
        )
        security_engine.register(
            PathTraversalSecurityValidator(
                base_url
            )
        )
        security_engine.register(
            SSRFSecurityValidator(
                base_url
            )
        )
        # ==========================================
        # ATTACK SURFACE ANALYSIS
        # ==========================================

        attack_surface = AttackSurfaceAnalyzer(
            security_engine
        )

        candidates = attack_surface.analyze(
            context.endpoints
        )

        console.print(
            "\n[bold cyan]Attack Surface[/bold cyan]"
        )

        for candidate in candidates:

            console.print(
                f"  [yellow]•[/yellow] "
                f"{candidate['vulnerability']} "
                f"→ "
                f"{candidate['method']} "
                f"{candidate['path']} "
                f""
                f"({candidate['parameter']})"
            )

        console.print(
            f"[green]✓[/green] "
            f"Potential tests: {len(candidates)}"
        )
        tools.register(
            SecurityTestTool(
                security_engine,
                context
            )
        )
        tools.register(
            RecordEvidenceTool(context)
        )

        tools.register(
            CreateFindingTool(context)
        )
        tools.register( ReadSourceTool(info.path) )
        tools.register(
            ListSourceFilesTool(info.path)
        )
        model = OpenRouterProvider()

        agent = SecurityAgent(
            model=model,
            tools=tools,
            context=context,
            attack_surface=candidates,
        )

        agent.run()

        console.print(
            "\n[bold green]✓ Agent execution completed[/bold green]"
        )

        console.print(
            f"Evidence collected: "
            f"{len(context.evidence)}"
        )

        console.print(
            f"Findings: "
            f"{len(context.findings)}"
        )

# ==========================================
# REPORTING
# ==========================================

        console.print(
            "\n[bold cyan]Generating Reports[/bold cyan]"
        )

        json_path = generate_json_report(
            context,
            "aegis-report.json",
        )

        markdown_path = generate_markdown_report(
            context,
            "aegis-report.md",
        )

        console.print(
            f"[green]✓[/green] JSON report: "
            f"{json_path}"
        )

        console.print(
            f"[green]✓[/green] Markdown report: "
            f"{markdown_path}"
        )

        if context.findings:

            console.print(
                "\n[bold red]Security Findings[/bold red]"
            )

            for finding in context.findings:

                console.print(
                    f"[red]●[/red] "
                    f"{finding.severity} — "
                    f"{finding.title} "
                    f"[{finding.confidence}]"
                )

        else:

            console.print(
                "\n[bold green]No confirmed findings.[/bold green]"
            )

        # Keep sandbox alive for testing
        console.print(
            "\n[dim]Press Ctrl+C to stop the sandbox.[/dim]"
        )

        try:

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            pass

    except Exception as e:

        console.print(
            f"\n[red]✗ Sandbox error:[/red] {e}"
        )

        raise typer.Exit(code=1)

    finally:

        sandbox.stop()


@app.command()
def version():
    """Show Aegis version."""

    console.print(
        "Aegis Security Scanner v0.1.0"
    )


if __name__ == "__main__":
    app()
