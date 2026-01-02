from src.infrastructure.exceptions.base_exceptions import InfrastructureException


class RateLimitExceeded(InfrastructureException):
    default_retryable = False
