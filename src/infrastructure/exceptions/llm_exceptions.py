from src.infrastructure.exceptions.base_exceptions import BaseCustomException


class LLMError(BaseCustomException):
    default_retryable = True


class LLMRateLimitError(LLMError):
    default_retryable = True


class LLMAuthError(LLMError):
    default_retryable = False
