import asyncio
from typing import Any

from src.application.ports.storage import Storage
from src.infrastructure.constants import TTL_FOR_STORAGE


class InMemoryStorage(Storage):
    """Fake async for compatibility."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self.ttl = TTL_FOR_STORAGE
        self._expiry_tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> dict[str, Any] | None:
        return self._data.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._data[key] = value
        if ttl:
            await self.expire(key, ttl)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)
        if key in self._expiry_tasks:
            self._expiry_tasks[key].cancel()
            del self._expiry_tasks[key]

    async def expire(self, key: str, ttl: int) -> None:
        if key in self._expiry_tasks:
            self._expiry_tasks[key].cancel()

        async def delete_after_ttl() -> None:
            await asyncio.sleep(ttl)
            self._data.pop(key, None)
            self._expiry_tasks.pop(key, None)

        self._expiry_tasks[key] = asyncio.create_task(delete_after_ttl())

    async def incr(self, key: str) -> int:
        async with self._lock:
            value = self._data.get(key, 0)

            if not isinstance(value, int):
                raise TypeError(
                    f"WRONGTYPE Operation against a key holding the wrong kind of value. "
                    f"Expected int, got {type(value).__name__}"
                )

            self._data[key] = value + 1
            new_value: int = self._data[key]
            return new_value

    async def incr_with_expire(self, key: str, ttl: int) -> int:
        async with self._lock:
            value = self._data.get(key, 0)

            if not isinstance(value, int):
                raise TypeError(
                    f"WRONGTYPE Operation against a key holding the wrong kind of value. "
                    f"Expected int, got {type(value).__name__}"
                )

            self._data[key] = value + 1
            new_value: int = self._data[key]

            await self.expire(key, ttl)
            return new_value
