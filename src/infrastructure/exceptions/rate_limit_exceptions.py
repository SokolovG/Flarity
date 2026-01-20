import logging

from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class RateLimitExceeded(InfrastructureException):
    default_retryable = False
    log_level = logging.INFO
