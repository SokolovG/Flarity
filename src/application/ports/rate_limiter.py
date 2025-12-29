from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    async def check_limit(self, key: str) -> bool: ...
    @abstractmethod
    async def reset(self, key: str) -> None: ...
