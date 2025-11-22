from src.exceptions.base_exceptions import BaseCustomException


class NetworkError(BaseCustomException):
    pass


class LokiError(BaseCustomException):
    pass


class LokiUnavailableError(LokiError):
    pass


class LogParsingError(LokiError):
    pass


class LLMError(BaseCustomException):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMAuthError(LLMError):
    pass
