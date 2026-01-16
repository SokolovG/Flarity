import asyncio
import time
from collections.abc import Callable, Coroutine
from functools import wraps
from logging import WARNING, getLogger
from typing import Any, ParamSpec, TypeVar

from src.domain.exceptions import DomainException
from src.infrastructure.exceptions.base_exceptions import InfrastructureException

T = TypeVar("T")
P = ParamSpec("P")

logger = getLogger(__name__)


def log_calls(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        parts = func.__qualname__.split(".")
        if len(parts) == 2:
            class_name, func_name = parts
            call_name = f"{class_name}.{func_name}"
        else:
            call_name = func.__qualname__

        logger.info(f"→ {call_name}()")

        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(f"✓ {call_name}() completed in {duration:.2f}s")
            return result

        except ValueError as e:
            duration = time.time() - start_time
            logger.warning(f"⚠ {call_name}() validation error in {duration:.2f}s: {e}")
            raise

        except DomainException as e:
            duration = time.time() - start_time
            level = getattr(e, "log_level", WARNING)
            logger.log(level, f"⚠ {call_name}() domain exception in {duration:.2f}s: {e.message}")
            raise

        except InfrastructureException as e:
            duration = time.time() - start_time
            logger.error(f"✗ {call_name}() infrastructure error in {duration:.2f}s: {e}")
            raise

        except Exception as e:
            duration = time.time() - start_time
            logger.exception(f"✗ {call_name}() unexpected error in {duration:.2f}s")
            raise

    return wrapper


def retry(
    max_attempts: int, backoff: float, max_backoff: float = 30.0
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

                    wait_time = min(backoff * (2**attempt), max_backoff)
                    logger.warning(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

        return wrapper

    return decorator
