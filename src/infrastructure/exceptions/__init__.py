from httpx import NetworkError

from src.infrastructure.exceptions.llm_exceptions import LLMAuthError, LLMError, LLMRateLimitError
from src.infrastructure.exceptions.loki_exceptions import (
    LogParsingError,
    LokiError,
    LokiUnavailableError,
)
from src.infrastructure.exceptions.telegram_exceptions import (
    TelegramBadRequestError,
    TelegramError,
    TelegramRateLimitError,
)

__all__ = [
    "BaseCustomException",
    "NetworkError",
    "LokiUnavailableError",
    "LogParsingError",
    "LLMRateLimitError",
    "LLMAuthError",
    "LLMError",
    "LokiError",
    "SettingsFieldIsEmpty",
    "TelegramBadRequestError",
    "TelegramError",
    "TelegramRateLimitError",
]
