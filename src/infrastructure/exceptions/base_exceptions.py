import logging
from typing import Any


class InfrastructureException(Exception):
    default_retryable: bool = False
    log_level = logging.ERROR

    def __init__(
        self,
        message: str,
        is_retryable: bool | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.is_retryable = is_retryable if is_retryable is not None else self.default_retryable
        self.details = details if details else {}
        super().__init__(message)
