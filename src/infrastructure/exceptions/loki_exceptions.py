from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class LokiError(InfrastructureException):
    default_retryable = True


class LokiUnavailableError(LokiError):
    default_retryable = True


class LogParsingError(LokiError):
    default_retryable = True
