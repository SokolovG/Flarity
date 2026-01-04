import asyncio

from src.application.ports.storage import Storage
from src.infrastructure.constants import RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD, RATE_LIMITER_PREFIX
from src.infrastructure.exceptions.rate_limit_exceptions import RateLimitExceeded


class RateLimiter:
    def __init__(self, storage: Storage) -> None:
        self.calls = RATE_LIMIT_CALLS
        self.period = RATE_LIMIT_PERIOD
        self.key_prefix = RATE_LIMITER_PREFIX
        self.storage = storage
        self._user_locks: dict[str, asyncio.Lock] = {}

    def acquire_user_lock(self, user_id: str) -> asyncio.Lock:
        if user_id not in self._user_locks:
            self._user_locks[user_id] = asyncio.Lock()
        return self._user_locks[user_id]

    async def check_limit(self, key: str) -> None:
        full_key = f"{self.key_prefix}{key}"
        current = await self.storage.incr_with_expire(full_key, self.period)

        if current > self.calls:
            raise RateLimitExceeded(f"Rate limit exceeded: {current}/{self.calls}")

    async def reset(self, key: str) -> None:
        await self.storage.delete(f"{self.key_prefix}{key}")
