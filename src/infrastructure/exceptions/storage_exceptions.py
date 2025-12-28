from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class StorageError(InfrastructureException):
    default_retryable = True
