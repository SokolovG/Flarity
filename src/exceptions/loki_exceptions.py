from src.exceptions.base_exceptions import BaseCustomException


class LokiError(BaseCustomException):
    default_retryable = True


class LokiUnavailableError(LokiError):
    default_retryable = True


class LogParsingError(LokiError):
    default_retryable = True
