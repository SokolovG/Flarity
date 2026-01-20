from msgspec import Struct

from src.domain.entities.enums import Status


class _LokiStream(Struct):
    stream: dict[str, str]
    values: list[tuple[str, str]]


class _LokiData(Struct):
    result: list[_LokiStream]


class LokiQueryRangeResponse(Struct):
    status: Status
    data: _LokiData
