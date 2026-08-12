from aegis.tools.registry import ToolRegistry
from aegis.tools.http import HTTPRequestTool


def test_tool_registry():

    registry = ToolRegistry()

    http_tool = HTTPRequestTool(
        "http://example.com"
    )

    registry.register(http_tool)

    tools = registry.list_tools()

    assert len(tools) == 1
    assert tools[0]["name"] == "http_request"


def test_http_tool():

    registry = ToolRegistry()

    registry.register(
        HTTPRequestTool(
            "http://example.com"
        )
    )

    result = registry.execute(
        "http_request",
        method="GET",
        path="/",
    )

    assert result.success is True
    assert result.output["status_code"] == 200