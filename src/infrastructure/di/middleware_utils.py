from collections.abc import Callable

from dishka.integrations.aiogram import wrap_injection  # type: ignore[attr-defined]

CONTAINER_KEY = "dishka_container"


def aiogram_middleware_inject(func: Callable) -> Callable:
    return wrap_injection(
        func=func,
        is_async=True,
        container_getter=lambda args, kwargs: args[3][CONTAINER_KEY],
    )
