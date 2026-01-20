import logging
from typing import Any


class DomainException(Exception):
    """Base domain exception"""

    log_level = logging.WARNING

    def __init__(self, message: str = "", details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details if details else {}


class AnalysisFailedError(DomainException):
    """Analysis failed Error"""

    log_level = logging.ERROR


class LLMChatLimitExceededError(DomainException):
    """User exceeded limit of questions per session"""

    log_level = logging.INFO
