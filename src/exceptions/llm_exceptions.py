from src.exceptions.base_exceptions import BaseCustomException


class LLMError(BaseCustomException):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMAuthError(LLMError):
    pass
