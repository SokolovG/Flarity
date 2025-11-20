from src.entities.enums import Status

from msgspec import Struct

from src.entities.loki import LogEntry


class LokiStream(Struct):
    stream: dict[str, str]
    values: list[tuple[str, str]]


class LokiData(Struct):
    result: list[LokiStream]


class LokiQueryRangeResponse(Struct):
    status: Status
    data: LokiData


class LokiQueryResult(Struct):
    logs: list[LogEntry]
    total_count: int


class LogGroupByErrorType(Struct):
    error: str
    logs: list[LogEntry]


class LogsByErrorType(Struct):
    logs_groups: list[LogGroupByErrorType]
    total_count: int
