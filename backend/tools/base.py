from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    name: str

    @abstractmethod
    def can_handle(self, instruction: str) -> bool:
        pass

    @abstractmethod
    def parse(self, instruction: str) -> dict:
        pass

    @abstractmethod
    def execute(self, params: dict) -> Any:
        pass
