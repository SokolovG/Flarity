from src.exceptions.base_exceptions import BaseCustomException


class NetworkError(BaseCustomException):
    default_retryable = True
