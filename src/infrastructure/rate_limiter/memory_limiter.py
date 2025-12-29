from src.application.ports.rate_limiter import RateLimiter


class InMemoryRateLimiter(RateLimiter):
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period

    async def check_limit(self, key: str) -> bool:
        return True

    async def reset(self, key: str) -> None:
        return
