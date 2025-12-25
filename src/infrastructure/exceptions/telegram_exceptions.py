from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class TelegramError(InfrastructureException):
    default_retryable = True


class TelegramRateLimitError(TelegramError):
    default_retryable = True


class TelegramBadRequestError(TelegramError):
    default_retryable = True
