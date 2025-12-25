from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class LLMError(InfrastructureException):
    default_retryable = True


class LLMRateLimitError(LLMError):
    default_retryable = True


class LLMAuthError(LLMError):
    default_retryable = False
