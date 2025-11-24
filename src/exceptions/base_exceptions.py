from typing import Any


class BaseCustomException(Exception):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.details = details if details else {}
        super().__init__(message)


class SettingsFieldIsEmpty(BaseCustomException):
    pass


class ServiceNotReadyError(Exception):
    pass
