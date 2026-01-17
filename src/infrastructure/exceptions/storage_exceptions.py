import logging

from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class StorageError(InfrastructureException):
    default_retryable = True
    log_level = logging.WARNING
