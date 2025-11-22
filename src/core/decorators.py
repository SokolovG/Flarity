from collections.abc import Callable, Coroutine
from functools import wraps
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


def handle_errors(
    func: Callable[P, Coroutine[Any, Any, T]],
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except NetworkError:
            ...
        except LLMError:
            ...
        except LLMRateLimitError:
            ...
        except LogParsingError:
            ...
        except LokiError:
            ...
        except LokiUnavailableError:
            ...
        except Exception:
            ...

    return wrapper


def handle_rate_limit() -> None: ...
