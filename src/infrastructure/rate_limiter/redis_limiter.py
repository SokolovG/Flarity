from typing import Final

from src.application.ports.storage import Storage

RATE_LIMITER_PREFIX: Final[str] = "rate_limit:"


class RateLimiter:
    def __init__(self, storage: Storage, calls: int, period: int) -> None:
        self.calls = calls
        self.period = period
        self.storage = storage

    async def check_limit(self, key: str) -> bool:
        # TODO: lua script?
        full_key = f"{RATE_LIMITER_PREFIX}{key}"
        current = await self.storage.incr(full_key)
        if current == 1:
            await self.storage.expire(full_key, self.period)

        return bool(current <= self.calls)

    async def reset(self, key: str) -> None:
        await self.storage.delete(f"{RATE_LIMITER_PREFIX}{key}")
