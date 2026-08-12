from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Parameter:
    name: str
    location: str
    value: Optional[str] = None


@dataclass
class Endpoint:
    path: str
    method: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    title: Optional[str] = None
    parameters: list[Parameter] = field(default_factory=list)


@dataclass
class ReconResult:
    base_url: str
    reachable: bool = False
    server: Optional[str] = None
    technologies: list[str] = field(default_factory=list)
    endpoints: list[Endpoint] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    javascript_files: list[str] = field(default_factory=list)


class ReconEngine:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def request(self, path: str = "/"):
        url = urljoin(self.base_url + "/", path.lstrip("/"))

        try:
            return requests.get(
                url,
                timeout=5,
                allow_redirects=True,
            )
        except requests.RequestException:
            return None

    def detect_server(self, response):
        if not response:
            return None

        return response.headers.get("Server")

    def detect_technologies(self, response):
        technologies = []

        if not response:
            return technologies

        headers = response.headers

        server = headers.get(
            "Server", ""
        ).lower()

        powered_by = headers.get(
            "X-Powered-By", ""
        ).lower()

        if "express" in powered_by:
            technologies.append("Express")

        if "node" in powered_by:
            technologies.append("Node.js")

        if "nginx" in server:
            technologies.append("Nginx")

        if "apache" in server:
            technologies.append("Apache")

        content_type = headers.get(
            "Content-Type", ""
        ).lower()

        if "application/json" in content_type:
            technologies.append("JSON API")

        return technologies

    def parse_html(self, response):
        """
        Extract links, forms and JavaScript files
        from an HTML response.
        """

        links = []
        javascript_files = []
        forms = []

        if not response:
            return links, javascript_files, forms

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "text/html" not in content_type:
            return links, javascript_files, forms

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # -------------------------
        # Links
        # -------------------------

        for tag in soup.find_all("a", href=True):

            url = urljoin(
                self.base_url + "/",
                tag["href"]
            )

            if url.startswith(self.base_url):
                links.append(url)

        # -------------------------
        # JavaScript
        # -------------------------

        for tag in soup.find_all(
            "script",
            src=True
        ):

            url = urljoin(
                self.base_url + "/",
                tag["src"]
            )

            if url.startswith(self.base_url):
                javascript_files.append(url)

        # -------------------------
        # Forms
        # -------------------------

        for form in soup.find_all("form"):

            action = form.get(
                "action",
                "/"
            )

            method = form.get(
                "method",
                "GET"
            ).upper()

            action_url = urljoin(
                self.base_url + "/",
                action
            )

            parameters = []

            for field in form.find_all(
                ["input", "textarea", "select"]
            ):

                name = field.get("name")

                if not name:
                    continue

                parameters.append(
                    Parameter(
                        name=name,
                        location="form",
                        value=field.get("value")
                    )
                )

            forms.append(
                Endpoint(
                    path=action_url.replace(
                        self.base_url,
                        ""
                    ) or "/",
                    method=method,
                    parameters=parameters
                )
            )

        return (
            links,
            javascript_files,
            forms
        )

    def discover_common_endpoints(self):

        common_paths = [
            "/",
            "/health",
            "/api",
            "/api/v1",
            "/login",
            "/register",
            "/admin",
            "/dashboard",
            "/search",
            "/users",
            "/profile",
            "/account",
            "/api/users",
            "/api/search",
            "/robots.txt",
            "/swagger",
            "/swagger.json",
            "/openapi.json",
        ]

        endpoints = []

        for path in common_paths:

            response = self.request(path)

            if response is None:
                continue

            if response.status_code == 404:
                continue

            content_type = response.headers.get(
                "Content-Type"
            )

            title = None

            if "text/html" in (content_type or ""):

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                if soup.title:
                    title = soup.title.string

            parameters = []

            # Try common, harmless parameter names.
            candidate_parameters = [
                "q",
                "query",
                "search",
                "id",
                "username",
                "name",
                "page",
            ]

            for parameter in candidate_parameters:

                test_response = self.request(
                    f"{path}?{parameter}=aegis_test"
                )

                if test_response is None:
                    continue

                # If the endpoint behaves differently when the
                # parameter is supplied, record it.
                if (
                    test_response.status_code
                    != response.status_code
                    or test_response.text
                    != response.text
                ):
                    parameters.append(
                        Parameter(
                            name=parameter,
                            location="query",
                            value="aegis_test",
                        )
                    )

            endpoints.append(
                Endpoint(
                    path=path,
                    method="GET",
                    status_code=response.status_code,
                    content_type=content_type,
                    title=title,
                    parameters=parameters,
                )
            )

        return endpoints

    def run(self):

        result = ReconResult(
            base_url=self.base_url
        )

        # -------------------------
        # Initial request
        # -------------------------

        response = self.request("/")

        if response is None:
            return result

        result.reachable = True

        result.server = self.detect_server(
            response
        )

        result.technologies = (
            self.detect_technologies(response)
        )

        # -------------------------
        # Parse homepage
        # -------------------------

        (
            links,
            javascript_files,
            forms
        ) = self.parse_html(response)

        result.links = list(
            dict.fromkeys(links)
        )

        result.javascript_files = list(
            dict.fromkeys(javascript_files)
        )

        # -------------------------
        # Common endpoints
        # -------------------------

        result.endpoints = (
            self.discover_common_endpoints()
        )

        # -------------------------
        # Add discovered forms
        # -------------------------

        existing = {
            (
                endpoint.path,
                endpoint.method
            )
            for endpoint in result.endpoints
        }

        for form in forms:

            key = (
                form.path,
                form.method
            )

            if key not in existing:
                result.endpoints.append(form)

        return result
