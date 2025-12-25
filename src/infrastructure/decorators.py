import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from logging import getLogger
from typing import Any, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")

logger = getLogger(__name__)


def log_calls(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            logger.info(f"{func.__name__} completed successfully")
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise

    return wrapper


def retry(
    max_attempts: int,
    backoff: float,
) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
    def decorator(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    should_retry = getattr(e, "is_retryable", False)
                    if not should_retry or attempt == max_attempts - 1:
                        raise

                    wait_time = backoff * (2**attempt)
                    logger.warning(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

        return wrapper

    return decorator
