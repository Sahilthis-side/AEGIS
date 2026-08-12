from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    success: bool
    output: Any
    error: str | None = None


class Tool(ABC):

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass