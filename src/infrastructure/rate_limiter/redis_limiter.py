from typing import Final

from redis.asyncio import Redis

from src.application.ports.rate_limiter import RateLimiter

RATE_LIMITER_PREFIX: Final[str] = "rate_limit:"


class RedisRateLimiter(RateLimiter):
    def __init__(self, redis: Redis, calls: int, period: int) -> None:
        self.redis = redis
        self.calls = calls
        self.period = period

    async def check_limit(self, key: str) -> bool:
        # TODO: lua script.
        full_key = f"{RATE_LIMITER_PREFIX}{key}"
        current = await self.redis.incr(full_key)
        if current == 1:
            await self.redis.expire(full_key, self.period)

        return bool(current <= self.calls)

    async def reset(self, key: str) -> None:
        await self.redis.delete(f"{RATE_LIMITER_PREFIX}{key}")
