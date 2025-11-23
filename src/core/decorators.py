import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from logging import getLogger
from typing import Any, ParamSpec, TypeVar

from src.exceptions import (
    LLMError,
    LLMRateLimitError,
    LogParsingError,
    LokiError,
    LokiUnavailableError,
    NetworkError,
)

T = TypeVar("T")
P = ParamSpec("P")

logger = getLogger(__name__)


def handle_errors(
    func: Callable[P, Coroutine[Any, Any, T]],
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception:
            ...

    return wrapper


def log_errors(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception:
            ...

    return wrapper


def retry(
    max_attempts: int,
    backoff: float,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
    def decorator(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    if not isinstance(e, retryable_exceptions):
                        raise
                    if attempt == max_attempts - 1:
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                        f"Retrying in {backoff * (attempt + 1)}s..."
                    )
                    await asyncio.sleep(backoff * (attempt + 1))

        return wrapper

    return decorator
