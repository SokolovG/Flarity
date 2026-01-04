from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class NetworkError(InfrastructureException):
    default_retryable = True
