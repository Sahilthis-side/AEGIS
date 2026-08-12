from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin
import os
import re
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

    def __init__(self,base_url: str,target_path: str | None = None,):
        self.base_url = base_url.rstrip("/")
        self.target_path = target_path

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
        for tag in soup.find_all("a", href=True):

            url = urljoin(
                self.base_url + "/",
                tag["href"]
            )

            if url.startswith(self.base_url):
                links.append(url)
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
            "/api/users",
            "/api/search",
            "/login",
            "/register",
            "/logout",
            "/admin",
            "/dashboard",
            "/profile",
            "/account",
            "/search",
            "/users",
            "/user",
            "/items",
            "/item",
            "/products",
            "/product",
            "/download",
            "/file",
            "/files",
            "/upload",
            "/document",
            "/documents",
            "/export",
            "/import",
            "/config",
            "/settings",
            "/swagger",
            "/swagger.json",
            "/openapi.json",
            "/robots.txt",
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
            candidate_parameters = [
                "q",
                "query",
                "search",
                "id",
                "user_id",
                "item_id",
                "username",
                "name",
                "page",
                "limit",
                "offset",
                "file",
                "path",
                "filename",
                "filepath",
                "document",
                "template",
                "url",
                "uri",
                "link",
                "redirect",
                "callback",
                "target",
                "type",
                "format",
                "sort",
                "filter",
            ]

            for parameter in candidate_parameters:

                test_response = self.request(
                    f"{path}?{parameter}=aegis_test"
                )

                if test_response is None:
                    continue
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
    def discover_source_endpoints(self):
        """
        Discover Express routes and their query parameters
        directly from application source code.
        """

        endpoints = []

        if not self.target_path:
            return endpoints
        source_files = []

        for root, _, files in os.walk(self.target_path):
            if "node_modules" in root:
                continue

            if ".git" in root:
                continue

            for filename in files:

                if filename.endswith(
                    (".js", ".jsx", ".ts", ".tsx")
                ):
                    source_files.append(
                        os.path.join(root, filename)
                    )
        route_pattern = re.compile(
            r"""
            \b
            (?:app|router)
            \.
            (get|post|put|patch|delete|head|options)
            \s*
            \(
            \s*
            ["'`]([^"'`]+)["'`]
            """,
            re.IGNORECASE | re.VERBOSE,
        )
        query_pattern = re.compile(
            r"""
            \b
            (?:req|request)
            \.
            query
            \.
            ([A-Za-z_][A-Za-z0-9_]*)
            """,
            re.IGNORECASE | re.VERBOSE,
        )
    
        for source_file in source_files:
    
            try:
    
                with open(
                    source_file,
                    "r",
                    encoding="utf-8",
                    errors="ignore",
                ) as file:
    
                    source = file.read()
    
            except OSError:
                continue
    
            routes = route_pattern.findall(source)
    
            parameters = sorted(
                set(
                    query_pattern.findall(source)
                )
            )
    
            for method, path in routes:
    
                endpoint_parameters = [
                    Parameter(
                        name=parameter,
                        location="query",
                    )
                    for parameter in parameters
                ]
    
                endpoints.append(
                    Endpoint(
                        path=path,
                        method=method.upper(),
                        parameters=endpoint_parameters,
                    )
                )
    
        return endpoints
    def run(self):

        result = ReconResult(
            base_url=self.base_url
        )
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
        result.endpoints = (
            self.discover_common_endpoints()
        )
        source_endpoints = (
            self.discover_source_endpoints()
        )
    
        existing = {
            (
                endpoint.method,
                endpoint.path,
            )
            for endpoint in result.endpoints
        }
    
        for endpoint in source_endpoints:
    
            key = (
                endpoint.method,
                endpoint.path,
            )
    
            if key not in existing:
    
                result.endpoints.append(
                    endpoint
                )
    
                existing.add(key)
    
            else:
                for existing_endpoint in result.endpoints:
    
                    if (
                        existing_endpoint.method
                        == endpoint.method
                        and
                        existing_endpoint.path
                        == endpoint.path
                    ):
    
                        existing_parameters = {
                            parameter.name
                            for parameter
                            in existing_endpoint.parameters
                        }
    
                        for parameter in endpoint.parameters:
    
                            if (
                                parameter.name
                                not in existing_parameters
                            ):
    
                                existing_endpoint.parameters.append(
                                    parameter
                                )
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
