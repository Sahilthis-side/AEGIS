from urllib.parse import quote

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from aegis.security.base import (
    ValidationResult,
    VulnerabilityValidator,
)


class XSSSecurityValidator(VulnerabilityValidator):

    name = "xss"

    description = (
        "Validate reflected cross-site scripting "
        "using HTTP reflection and isolated browser "
        "execution."
    )

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def test(
        self,
        path: str,
        parameter: str,
    ) -> ValidationResult:

        marker = "AEGIS_XSS_7f3c91"

        payload = (
            "<script>"
            f"document.title='{marker}'"
            "</script>"
        )

        url = f"{self.base_url}{path}"
        try:
            response = requests.get(
                url,
                params={
                    parameter: payload,
                },
                timeout=10,
            )

        except requests.RequestException as error:

            return ValidationResult(
                vulnerability=self.name,
                status="insufficient_evidence",
                confidence="none",
                title="XSS Validation Failed",
                description=(
                    "The XSS validation request "
                    "could not be completed."
                ),
                evidence=[],
                details={
                    "error": str(error),
                },
            )

        body = response.text

        reflected = payload in body

        content_type = (
            response.headers
            .get("content-type", "")
            .lower()
        )

        if not reflected:

            return ValidationResult(
                vulnerability=self.name,
                status="not_confirmed",
                confidence="high",
                title="XSS Not Confirmed",
                description=(
                    "The controlled XSS payload "
                    "was not reflected."
                ),
                evidence=[
                    "Controlled payload was not "
                    "reflected in the response."
                ],
                details={
                    "endpoint": path,
                    "parameter": parameter,
                    "status_code": response.status_code,
                    "reflected": False,
                },
            )

        if "text/html" not in content_type:

            return ValidationResult(
                vulnerability=self.name,
                status="insufficient_evidence",
                confidence="medium",
                title="Potential Reflected XSS",
                description=(
                    "The payload was reflected, but "
                    "the response was not identified "
                    "as HTML."
                ),
                evidence=[
                    "Payload was reflected.",
                    f"Content-Type: {content_type}",
                ],
                details={
                    "endpoint": path,
                    "parameter": parameter,
                    "reflected": True,
                    "content_type": content_type,
                },
            )
        browser_result = self._browser_test(
            url=url,
            parameter=parameter,
            payload=payload,
            marker=marker,
        )

        if browser_result["executed"]:

            return ValidationResult(
                vulnerability=self.name,
                status="confirmed",
                confidence="high",
                title=(
                    "Reflected Cross-Site Scripting "
                    "(XSS)"
                ),
                description=(
                    "The controlled XSS payload was "
                    "reflected into an HTML response "
                    "and JavaScript execution was "
                    "confirmed in an isolated Chromium "
                    "browser."
                ),
                evidence=[
                    "Payload was reflected in HTML.",
                    (
                        "Browser execution marker was "
                        "observed."
                    ),
                    (
                        f"Marker: {marker}"
                    ),
                ],
                details={
                    "endpoint": path,
                    "parameter": parameter,
                    "reflected": True,
                    "browser_execution": True,
                    "marker": marker,
                    "status_code": response.status_code,
                    "content_type": content_type,
                },
                remediation=(
                    "HTML-encode untrusted input before "
                    "inserting it into HTML. Prefer "
                    "templating systems with automatic "
                    "output escaping."
                ),
            )

        return ValidationResult(
            vulnerability=self.name,
            status="insufficient_evidence",
            confidence="medium",
            title="Potential Reflected XSS",
            description=(
                "The payload was reflected into an "
                "HTML response, but browser execution "
                "could not be confirmed."
            ),
            evidence=[
                "Payload was reflected in HTML.",
                (
                    "Browser execution marker was "
                    "not observed."
                ),
            ],
            details={
                "endpoint": path,
                "parameter": parameter,
                "reflected": True,
                "browser_execution": False,
                "browser_error": browser_result.get(
                    "error"
                ),
            },
            remediation=(
                "HTML-encode untrusted input before "
                "inserting it into HTML."
            ),
        )

    def _browser_test(
        self,
        url: str,
        parameter: str,
        payload: str,
        marker: str,
    ) -> dict:

        try:

            with sync_playwright() as playwright:

                browser = playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )

                page = browser.new_page()

                executed = False

                def on_title(title: str):
                    nonlocal executed

                    if marker in title:
                        executed = True

                page.on(
                    "domcontentloaded",
                    lambda: None,
                )

                page.goto(
                    self._build_url(
                        url,
                        parameter,
                        payload,
                    ),
                    wait_until="domcontentloaded",
                    timeout=10000,
                )

                try:
                    page.wait_for_function(
                        f"""
                        () => document.title.includes(
                            "{marker}"
                        )
                        """,
                        timeout=3000,
                    )

                    executed = True

                except PlaywrightTimeoutError:
                    pass

                title = page.title()

                if marker in title:
                    executed = True

                browser.close()

                return {
                    "executed": executed,
                    "title": title,
                }

        except Exception as error:

            return {
                "executed": False,
                "error": str(error),
            }

    @staticmethod
    def _build_url(
        url: str,
        parameter: str,
        payload: str,
    ) -> str:

        separator = "&" if "?" in url else "?"

        return (
            f"{url}"
            f"{separator}"
            f"{quote(parameter)}="
            f"{quote(payload)}"
        )