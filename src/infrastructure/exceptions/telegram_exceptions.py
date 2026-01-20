import logging

from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class TelegramError(InfrastructureException):
    default_retryable = True
    log_level = logging.ERROR


class TelegramRateLimitError(TelegramError):
    default_retryable = True
    log_level = logging.WARNING


class TelegramBadRequestError(TelegramError):
    default_retryable = True
    log_level = logging.ERROR
