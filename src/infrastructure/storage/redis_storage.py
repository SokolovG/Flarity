from typing import Any

from src.application.ports.session_storage import SessionStorage


class RedisStorage(SessionStorage):
    async def get(self, key: str) -> Any: ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    async def delete(self, key: str) -> None: ...
