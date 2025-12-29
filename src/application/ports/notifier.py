from abc import ABC, abstractmethod
from typing import Any

from src.infrastructure.dto import BaseInfrastructureObject


class Notifier(ABC):
    @abstractmethod
    async def send(self, message: str, **kwargs: Any) -> BaseInfrastructureObject: ...
