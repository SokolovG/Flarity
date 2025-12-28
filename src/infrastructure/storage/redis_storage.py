from typing import Any

from redis import Redis

from src.application.ports.session_storage import SessionStorage


class RedisStorage(SessionStorage):
    def __init__(self, redis_client: Redis) -> None:
        self.client = redis_client

    async def get(self, key: str) -> Any: ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    async def update(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    async def delete(self, key: str) -> None: ...
