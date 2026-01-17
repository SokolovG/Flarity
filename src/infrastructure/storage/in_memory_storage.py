import asyncio
import time
from logging import getLogger
from typing import Any

from src.application.ports.storage import Storage
from src.infrastructure.constants import TTL_FOR_STORAGE
from src.infrastructure.exceptions.storage_exceptions import StorageTypeError

logger = getLogger(__name__)


class InMemoryStorage(Storage):
    """Fake async for compatibility."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self.ttl = TTL_FOR_STORAGE
        self._expiry_tasks: dict[str, tuple[asyncio.Task, float]] = {}
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
            task, _ = self._expiry_tasks[key]
            task.cancel()
            del self._expiry_tasks[key]

    async def expire(self, key: str, ttl: int) -> None:
        if key in self._expiry_tasks:
            task, _ = self._expiry_tasks[key]
            task.cancel()

        expiry_timestamp = time.time() + ttl

        async def delete_after_ttl() -> None:
            await asyncio.sleep(ttl)
            self._data.pop(key, None)
            self._expiry_tasks.pop(key, None)

        self._expiry_tasks[key] = (asyncio.create_task(delete_after_ttl()), expiry_timestamp)

    async def incr(self, key: str) -> int:
        async with self._lock:
            value = self._data.get(key, 0)

            if not isinstance(value, int):
                logger.error(
                    f"Invalid type for key {key}: expected int, got {type(value).__name__}"
                )
                raise StorageTypeError(
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
                logger.error(
                    f"Invalid type for key {key}: expected int, got {type(value).__name__}"
                )
                raise StorageTypeError(
                    f"WRONGTYPE Operation against a key holding the wrong kind of value. "
                    f"Expected int, got {type(value).__name__}"
                )

            self._data[key] = value + 1
            new_value: int = self._data[key]

            await self.expire(key, ttl)
            return new_value

    async def get_remaining_ttl(self, key: str) -> int | None:
        tple = self._expiry_tasks.get(key)
        if not tple:
            return None

        _, ttl_timestamp = self._expiry_tasks[key]
        ttl = int(ttl_timestamp - time.time())
        return ttl if ttl > 0 else None
