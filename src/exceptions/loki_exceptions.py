from src.exceptions.base_exceptions import BaseCustomException


class LokiError(BaseCustomException):
    pass


class LokiUnavailableError(LokiError):
    pass


class LogParsingError(LokiError):
    pass
