from typing import Any


class BaseCustomException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details if details else {}
        super().__init__(message)


class SettingsFieldIsEmpty(BaseCustomException):
    pass
