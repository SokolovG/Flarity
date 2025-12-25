from src.infrastructure.exceptions.base_exceptions import BaseCustomException


class TelegramError(BaseCustomException):
    default_retryable = True


class TelegramRateLimitError(TelegramError):
    default_retryable = True


class TelegramBadRequestError(TelegramError):
    default_retryable = True
