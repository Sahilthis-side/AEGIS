# Aegis

### AI-Powered Autonomous Application Security Scanner

Aegis is an AI-driven application security scanner designed to automatically analyze, test, validate, and report security vulnerabilities in local applications.

Instead of relying purely on static analysis or blindly generating vulnerability reports, Aegis combines:

- Source-code reconnaissance
- HTTP reconnaissance
- Attack-surface analysis
- AI-driven investigation
- Deterministic security validators
- Isolated Docker sandboxing
- Evidence collection
- Confirmed vulnerability findings
- JSON and Markdown reporting

The core design principle is simple:

> **Aegis should not report a vulnerability just because it looks suspicious. It should attempt to validate it and produce concrete evidence before creating a finding.**

---

## Current Status

Aegis is currently under active development.

### Supported Vulnerability Classes

| Vulnerability | Detection | Deterministic Validation | Finding |
|---|---:|---:|---:|
| SQL Injection | ✅ | ✅ | ✅ |
| Cross-Site Scripting (XSS) | ✅ | ✅ | ✅ |
| Path Traversal | ✅ | ✅ | ✅ |
| Server-Side Request Forgery (SSRF) | ✅ | ✅ | ✅ |

Aegis also supports source-aware endpoint discovery for JavaScript/TypeScript applications.

---

# Architecture

Aegis follows a multi-stage security analysis pipeline:

```text
                    ┌─────────────────────┐
                    │       Target        │
                    │  Local Application  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Target Detection  │
                    │                     │
                    │ Language            │
                    │ Framework           │
                    │ Package Manager     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Docker Sandbox    │
                    │                     │
                    │ Isolated Application│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Reconnaissance    │
                    │                     │
                    │ HTTP + Source Code  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Attack Surface    │
                    │      Analysis       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Security Agent   │
                    │                     │
                    │ AI Investigation    │
                    │ Tool Selection      │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │     Deterministic Validators   │
              │                                 │
              │ SQLi │ XSS │ SSRF │ Traversal │
              └────────────────┬────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Evidence Store    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Confirmed Findings  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Reports        │
                    │                     │
                    │ JSON + Markdown     │
                    └─────────────────────┘
```

---

# Why Aegis?

Traditional security scanners can produce large numbers of potential vulnerabilities that still require manual verification.

Aegis takes a different approach.

The AI agent can investigate an application, inspect its source code, select security tools, perform tests, collect evidence, and request deterministic validation.

A vulnerability becomes a formal finding only after the validation layer confirms it.

For example:

```text
Suspicious source code
        ↓
AI investigation
        ↓
Security test
        ↓
Deterministic validator
        ↓
Confirmed
        ↓
Evidence
        ↓
Finding
```

If validation fails:

```text
Suspicious source code
        ↓
Security test
        ↓
Not confirmed
        ↓
No finding
```

This separation between **hypothesis** and **validated finding** is one of the central design principles of Aegis.

---

# Features

## AI Security Agent

The security agent can:

- Inspect application source code
- Select available security tools
- Analyze discovered endpoints
- Run security tests
- Record evidence
- Create validated findings
- Stop when the investigation is complete

The agent operates through a controlled tool registry rather than having unrestricted access to the application.

---

## Isolated Docker Sandbox

Target applications are executed inside a Docker sandbox.

The general flow is:

```text
Local Target
     ↓
Docker Sandbox
     ↓
Install Dependencies
     ↓
Start Application
     ↓
Health Check
     ↓
Security Testing
```

This allows Aegis to test applications in an isolated environment rather than directly executing arbitrary target applications on the host system.

---

## Source-Aware Reconnaissance

Aegis performs both runtime and source-level reconnaissance.

For JavaScript/TypeScript applications, it can identify Express-style routes such as:

```javascript
app.get("/fetch", ...)
app.get("/download", ...)
```

and query parameters such as:

```javascript
req.query.url
req.query.file
```

This allows the scanner to build a broader attack surface before the AI investigation begins.

---

## HTTP Reconnaissance

Aegis also interacts with the running application to identify reachable endpoints and their behavior.

It can inspect:

- HTTP status codes
- Content types
- HTML links
- Forms
- JavaScript files
- Query parameters
- Application technologies

---

## Deterministic Validation

Aegis separates AI reasoning from vulnerability confirmation.

Security validators currently exist for:

### SQL Injection

Tests whether user-controlled parameters can influence database queries.

### Cross-Site Scripting

Uses controlled payloads and browser execution verification to determine whether injected JavaScript actually executes.

### Path Traversal

Tests whether user-controlled filesystem paths can escape their intended directory.

### SSRF

Tests whether user-controlled URLs can cause the application to access internal services.

---

# Confirmed Findings

Aegis does not automatically turn every AI hypothesis into a vulnerability.

The `create_finding` tool requires the corresponding validator to have returned:

```text
status = confirmed
```

For example:

```text
Security Test
     ↓
Validator
     ↓
confirmed
     ↓
Evidence
     ↓
Create Finding
```

This prevents the AI agent from simply claiming that a vulnerability exists without validation.

---

# Project Structure

```text
AEGIS/
│
├── .gitignore
│
└── aegis/
    │
    ├── aegis/
    │   │
    │   ├── agents/
    │   │   ├── __init__.py
    │   │   ├── agent.py
    │   │   ├── model.py
    │   │   └── mock.py
    │   │
    │   ├── config/
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   │
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── context.py
    │   │   ├── detector.py
    │   │   ├── models.py
    │   │   └── recon.py
    │   │
    │   ├── providers/
    │   │   ├── anthropic.py
    │   │   ├── gemini.py
    │   │   ├── openai.py
    │   │   └── openrouter.py
    │   │
    │   ├── reporting/
    │   │   ├── __init__.py
    │   │   ├── json_report.py
    │   │   └── markdown.py
    │   │
    │   ├── sandbox/
    │   │   ├── __init__.py
    │   │   └── docker.py
    │   │
    │   ├── security/
    │   │   ├── __init__.py
    │   │   ├── attack_surface.py
    │   │   ├── base.py
    │   │   ├── engine.py
    │   │   ├── sqli.py
    │   │   ├── xss.py
    │   │   ├── path_traversal.py
    │   │   ├── ssrf.py
    │   │   └── validators/
    │   │       ├── base.py
    │   │       └── registry.py
    │   │
    │   ├── tools/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── registry.py
    │   │   ├── evidence.py
    │   │   ├── finding.py
    │   │   ├── files.py
    │   │   ├── http.py
    │   │   ├── shell.py
    │   │   ├── source.py
    │   │   ├── security.py
    │   │   ├── sqli.py
    │   │   ├── path_traversal.py
    │   │   └── ssrf.py
    │   │
    │   └── cli.py
    │
    ├── labs/
    │   │
    │   ├── sqli/
    │   │   ├── package.json
    │   │   ├── package-lock.json
    │   │   └── server.js
    │   │
    │   ├── xss/
    │   │   ├── package.json
    │   │   ├── package-lock.json
    │   │   └── server.js
    │   │
    │   ├── path-traversal/
    │   │   ├── package.json
    │   │   ├── package-lock.json
    │   │   └── server.js
    │   │
    │   └── ssrf/
    │       ├── package.json
    │       ├── package-lock.json
    │       └── server.js
    │
    ├── tests/
    │   ├── test_provider.py
    │   └── test_tools.py
    │
    ├── pyproject.toml
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── LICENSE
```

---

# Directory Overview

## `aegis/aegis/core/`

Contains the core scanner infrastructure.

### `context.py`

Maintains the state of a scan, including:

- Target information
- Technologies
- Endpoints
- Links
- JavaScript files
- Evidence
- Findings
- Validation results

### `detector.py`

Detects the target application's:

- Programming language
- Framework
- Package manager
- Start command

### `recon.py`

Responsible for application reconnaissance.

It performs:

- Runtime HTTP discovery
- Source-aware endpoint discovery
- Parameter discovery
- Technology detection
- Link discovery
- Form discovery
- JavaScript discovery

---

# `aegis/aegis/agents/`

Contains the AI security agent.

### `agent.py`

Controls the investigation loop:

```text
Think
 ↓
Select Tool
 ↓
Execute Tool
 ↓
Observe Result
 ↓
Think Again
```

### `model.py`

Defines the model interface used by the agent.

### `mock.py`

Provides a mock agent/model implementation for development and testing.

---

# `aegis/aegis/security/`

Contains vulnerability validation and attack-surface logic.

### `engine.py`

The central vulnerability validation engine.

Validators are registered with the engine and can then be executed by vulnerability name.

Current vulnerability types include:

```text
sql_injection
xss
path_traversal
ssrf
```

### `base.py`

Defines:

- `ValidationResult`
- `VulnerabilityValidator`

### `attack_surface.py`

Analyzes discovered endpoints and identifies potential security tests.

### Vulnerability Validators

```text
sqli.py
xss.py
path_traversal.py
ssrf.py
```

These connect the generic security engine with deterministic vulnerability-specific validation logic.

---

# `aegis/aegis/tools/`

Contains tools available to the AI security agent.

Examples include:

```text
http.py
source.py
files.py
shell.py
security.py
evidence.py
finding.py
```

The `registry.py` file controls which tools are available to the agent.

This provides a controlled interface between the AI model and Aegis capabilities.

---

# `aegis/aegis/sandbox/`

Contains Docker sandbox functionality.

### `docker.py`

Responsible for:

- Creating the sandbox
- Starting the target
- Installing dependencies
- Mapping ports
- Performing health checks
- Stopping/removing the sandbox

---

# `aegis/aegis/providers/`

Contains model provider integrations.

Current provider implementations include:

```text
OpenAI
OpenRouter
Gemini
Anthropic
```

The active provider is selected through the application's configuration.

---

# `aegis/aegis/reporting/`

Contains report generators.

### JSON

Produces:

```text
aegis-report.json
```

### Markdown

Produces:

```text
aegis-report.md
```

Reports contain scan information, evidence, and confirmed findings.

---

# `labs/`

The `labs` directory contains **intentionally vulnerable applications used for testing Aegis**.

These are not production applications.

They exist so developers can verify that Aegis is actually capable of finding and validating vulnerabilities.

Current labs:

```text
labs/
├── sqli/
├── xss/
├── path-traversal/
└── ssrf/
```

Each lab is an independent Node.js/Express application with intentionally vulnerable behavior.

For example:

```text
labs/ssrf/
├── package.json
├── package-lock.json
└── server.js
```

The SSRF lab contains an intentionally exposed internal service so that Aegis can prove that the vulnerability is exploitable.

---

# Requirements

Before installing Aegis, make sure you have:

- Python 3.10+
- Git
- Node.js and npm
- Docker Desktop
- An API key for a supported LLM provider

Docker must be running before starting a scan.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Sahilthis-side/AEGIS.git
cd AEGIS
```

---

## 2. Create a Python Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Aegis

From the repository root:

```bash
pip install -e aegis
```

Verify the installation:

```bash
aegis version
```

Expected:

```text
Aegis Security Scanner v0.1.0
```

---

# Configuration

Aegis uses environment variables for model provider configuration.

Copy the example configuration.

### Windows

```powershell
copy aegis\.env.example aegis\.env
```

### Linux/macOS

```bash
cp aegis/.env.example aegis/.env
```

Then edit:

```text
aegis/.env
```

Example:

```env
OPENAI_API_KEY=
OPENAI_MODEL=

GEMINI_API_KEY=
GEMINI_MODEL=

OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=
```

You only need to configure the provider you intend to use.

**Never commit `.env` to Git.**

Use `.env.example` when sharing configuration templates.

---

# Docker Setup

Aegis uses Docker to isolate target applications.

Make sure Docker Desktop is running.

Verify:

```bash
docker --version
```

Then:

```bash
docker ps
```

If Docker is working, Aegis should be able to create a sandbox automatically during a scan.

---

# Running Aegis

The basic command is:

```bash
aegis scan <target>
```

For example:

```bash
aegis scan labs/ssrf
```

On Windows:

```powershell
aegis scan labs\ssrf
```

Aegis will:

1. Detect the target
2. Create a Docker sandbox
3. Install dependencies
4. Start the application
5. Wait for the application to become healthy
6. Perform HTTP reconnaissance
7. Perform source-aware reconnaissance
8. Build the attack surface
9. Start the AI security agent
10. Execute security tests
11. Validate vulnerabilities
12. Collect evidence
13. Create confirmed findings
14. Generate reports

---

# Example Scan

Running:

```bash
aegis scan labs/ssrf
```

will produce output similar to:

```text
╔══════════════════════════════════╗
║       AEGIS SECURITY SCANNER     ║
╚══════════════════════════════════╝

Target detected

Sandbox
✓ Docker connection established
✓ Sandbox created
✓ Dependencies installed
✓ Application started
✓ Application health check passed

✓ TARGET READY

Reconnaissance
✓ Target is reachable

Discovered Endpoints

GET /fetch    url

Attack Surface

• ssrf → GET /fetch (url)

Security Agent

[Agent] Tool: security_test
[Tool] Success

[Agent] Tool: create_finding
[Tool] Success

Security Findings

● high — Server-Side Request Forgery (SSRF)
```

---

# Testing the Included Labs

The included labs can be used to test individual vulnerability classes.

## SQL Injection Lab

```bash
aegis scan labs/sqli
```

Expected result:

```text
SQL Injection
Severity: High
Confidence: High
```

---

## XSS Lab

```bash
aegis scan labs/xss
```

Expected result:

```text
Reflected Cross-Site Scripting (XSS)
Severity: High
Confidence: High
```

---

## Path Traversal Lab

```bash
aegis scan labs/path-traversal
```

Expected result:

```text
Path Traversal
Severity: High
Confidence: High
```

---

## SSRF Lab

```bash
aegis scan labs/ssrf
```

Expected result:

```text
Server-Side Request Forgery (SSRF)
Severity: High
Confidence: High
```

---

# Reports

After a scan, Aegis generates:

```text
aegis-report.json
aegis-report.md
```

The JSON report is useful for:

- Automation
- CI/CD
- Programmatic processing
- Future dashboards
- Machine-readable security results

The Markdown report is useful for:

- Human review
- Security reports
- Documentation
- Sharing findings

---

# Development

Clone the repository:

```bash
git clone https://github.com/Sahilthis-side/AEGIS.git
cd AEGIS
```

Create the development environment:

```bash
python -m venv .venv
```

Activate it.

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install in editable mode:

```bash
pip install -e aegis
```

Run tests:

```bash
pytest
```

Run the scanner:

```bash
aegis scan labs/ssrf
```

---

# Git Branches

Aegis uses two primary branches:

```text
main
 │
 └── Stable releases

develop
 │
 └── Active development
```

New features should generally be developed on `develop` before being promoted to `main`.

---

# Security Model

Aegis is intended to be used against applications that you own or are explicitly authorized to test.

The included applications under `labs/` are intentionally vulnerable and exist specifically for security testing.

Do not use Aegis against systems without authorization.

---

# Design Principles

Aegis is being built around several principles.

## 1. Evidence Over Assumptions

A suspicious code pattern should not automatically become a vulnerability finding.

## 2. AI for Investigation

The AI agent is responsible for reasoning, exploration, tool selection, and investigation.

## 3. Deterministic Validation

Security validators provide an independent confirmation layer.

## 4. Isolated Execution

Target applications should run inside a controlled sandbox.

## 5. Developer-First Workflow

Aegis should eventually be usable as easily as:

```bash
aegis scan ./my-application
```

## 6. Extensible Architecture

New vulnerability classes should be addable without rewriting the entire scanner.

The intended extension model is:

```text
New Vulnerability
       ↓
Security Validator
       ↓
Security Tool
       ↓
Engine Registration
       ↓
Attack Surface
       ↓
AI Agent
       ↓
Finding
```

---

# Roadmap

Aegis is actively evolving.

### Security Analysis

- [x] SQL Injection validation
- [x] Cross-Site Scripting validation
- [x] Path Traversal validation
- [x] SSRF validation
- [x] Deterministic validation engine
- [x] Evidence collection
- [x] Confirmed finding system
- [x] Source-aware endpoint discovery
- [ ] Additional vulnerability classes
- [ ] Improved source-code analysis
- [ ] JavaScript/TypeScript data-flow analysis
- [ ] Authentication-aware testing
- [ ] API schema discovery
- [ ] OpenAPI support
- [ ] Multi-step attack chains
- [ ] Improved evidence correlation

### Browser Security

- [x] Chromium-based XSS validation
- [ ] Advanced browser instrumentation
- [ ] DOM-based XSS analysis
- [ ] Client-side security testing

### Sandbox

- [x] Docker application sandbox
- [x] Automatic dependency installation
- [x] Automatic application startup
- [x] Health checking
- [ ] Stronger sandbox isolation
- [ ] Resource limits
- [ ] Network policy controls

### Reporting

- [x] JSON reports
- [x] Markdown reports
- [ ] SARIF reports
- [ ] HTML reports
- [ ] Security dashboard
- [ ] CI/CD integrations

### AI Agent

- [x] Tool-based investigation
- [x] Tool result feedback
- [x] Security testing workflow
- [x] Evidence-driven findings
- [ ] Multi-agent security teams
- [ ] Attack-chain reasoning
- [ ] Adaptive exploration
- [ ] Long-running autonomous assessments

---

# Contributing

Contributions are welcome.

A good contribution should generally:

1. Add or improve a clearly defined capability.
2. Include tests where appropriate.
3. Avoid introducing secrets or credentials.
4. Keep security validators deterministic where possible.
5. Document new vulnerability classes or tools.
6. Include a test lab when introducing a new vulnerability class.

For a new vulnerability type, the preferred development workflow is:

```text
Create Vulnerable Lab
        ↓
Implement Validator
        ↓
Register Validator
        ↓
Implement Agent Tool
        ↓
Add Attack-Surface Logic
        ↓
Run End-to-End Scan
        ↓
Verify Evidence
        ↓
Verify Finding
        ↓
Add Tests
```

---

# Adding a New Vulnerability

Aegis is designed to make vulnerability classes modular.

A typical new vulnerability should contain:

```text
security/
└── new_vulnerability.py

tools/
└── new_vulnerability.py

labs/
└── new-vulnerability/
    ├── package.json
    ├── package-lock.json
    └── server.js
```

The validator should return a structured `ValidationResult`.

For example:

```python
ValidationResult(
    vulnerability="example",
    status="confirmed",
    confidence="high",
    title="Example Vulnerability",
    description="...",
    evidence=["..."],
    details={},
    remediation="...",
)
```

Only confirmed validation results should be allowed to become formal findings.

---

# Project Philosophy

Aegis is not intended to be another static vulnerability pattern matcher.

The long-term goal is to build an autonomous security system that can:

```text
Understand
    ↓
Explore
    ↓
Hypothesize
    ↓
Test
    ↓
Validate
    ↓
Prove
    ↓
Report
```

The AI should be able to investigate applications dynamically while deterministic security components provide the final layer of trust.

---

# Disclaimer

Aegis is a security research and defensive testing tool.

Only scan applications and systems that you own or have explicit authorization to test.

The vulnerable applications under `labs/` are intentionally insecure and should only be run in controlled environments.

The authors are not responsible for misuse of this software.

---

# License

This project is licensed under the terms specified in MIT.

---

# Acknowledgements

Aegis is being developed as an open-source security research project focused on combining AI agents, application security testing, deterministic validation, and sandboxed execution.

---

## Aegis

**AI-powered application security testing with evidence-backed findings.**