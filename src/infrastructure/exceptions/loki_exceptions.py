import logging

from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class LokiError(InfrastructureException):
    default_retryable = True
    log_level = logging.ERROR


class LokiUnavailableError(LokiError):
    default_retryable = True
    log_level = logging.WARNING
