from httpx import NetworkError

from src.core.exceptions.base_exceptions import (
    BaseCustomException,
    ServiceNotReadyError,
    SettingsFieldIsEmpty,
)
from src.core.exceptions.llm_exceptions import LLMAuthError, LLMError, LLMRateLimitError
from src.core.exceptions.loki_exceptions import LogParsingError, LokiError, LokiUnavailableError
from src.core.exceptions.telegram_exceptions import (
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
    "ServiceNotReadyError",
    "TelegramBadRequestError",
    "TelegramError",
    "TelegramRateLimitError",
]
