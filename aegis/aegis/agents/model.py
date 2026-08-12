from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AgentResponse:

    message: str = ""

    tool_name: str | None = None

    tool_arguments: dict[str, Any] | None = None

    finished: bool = False

    provider_data: Any = None


class AgentModel(ABC):

    @abstractmethod
    def think(
        self,
        context: dict[str, Any],
        tools: list[dict[str, Any]],
    ) -> AgentResponse:
        pass

    def observe_tool_result(
        self,
        response: AgentResponse,
        result: Any,
    ):
        """
        Give the provider the result of a tool call.

        Providers that maintain conversation history
        can override this method.
        """
        pass