from msgspec import Struct

from src.entities.enums import Status


class LLMResponse(Struct):
    status: Status
    data: str
