import asyncio
from weakref import WeakValueDictionary

from src.application.ports.storage import Storage
from src.infrastructure.decorators import log_calls
from src.infrastructure.exceptions.rate_limit_exceptions import RateLimitExceeded


class RateLimiter:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self._user_locks: WeakValueDictionary[str, asyncio.Lock] = WeakValueDictionary()

    def acquire_user_lock(self, user_id: str) -> asyncio.Lock:
        lock = self._user_locks.get(user_id)
        if lock is None:
            lock = asyncio.Lock()
            self._user_locks[user_id] = lock

        return lock

    @log_calls
    async def check_limit(self, key: str, prefix: str, calls: int, period: int) -> None:
        full_key = f"{prefix}{key}"
        current = await self.storage.incr_with_expire(full_key, period)

        if current > calls:
            ttl = self.get_remaining_ttl(full_key)
            msg = f"Rate limit exceeded: {current}/{calls}.\n"

            raise RateLimitExceeded(msg, details={"ttl": ttl})

    async def reset(self, key: str, prefix: str) -> None:
        await self.storage.delete(f"{prefix}{key}")

    async def get_remaining_ttl(self, key: str) -> int | None:
        ttl: int | None = await self.storage.get_remaining_ttl(key)
        return ttl
