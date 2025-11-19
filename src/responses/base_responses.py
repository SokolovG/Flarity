from typing import Any
import msgspec


class BaseResponse(msgspec.Struct): ...


class ErrorResponse(msgspec.Struct):
    error_code: str
    message: str
    success: bool = False
    details: Any | None = None
