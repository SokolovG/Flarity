import logging

from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class LLMError(InfrastructureException):
    default_retryable = True


class LLMRateLimitError(LLMError):
    default_retryable = True
    log_level = logging.WARNING


class LLMAuthError(LLMError):
    default_retryable = False
    log_level = logging.ERROR
