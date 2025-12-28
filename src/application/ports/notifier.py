from abc import ABC, abstractmethod
from typing import Any

from src.infrastructure.entities import BaseMessageObject


class Notifier(ABC):
    @abstractmethod
    async def send(self, message: str, **kwargs: Any) -> BaseMessageObject: ...
