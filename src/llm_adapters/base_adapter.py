from abc import ABC, abstractmethod


class BaseLLMAdapter(ABC):
    @abstractmethod
    async def anylize_logs(self) -> None: ...
