from msgspec import Struct

from src.domain.entities.log_entry import LogEntry


class LogsSourceQueryResult(Struct):
    logs: list[LogEntry]
    total_count: int


class LogGroupByErrorType(Struct):
    error: str
    logs: list[LogEntry]


class LogsByErrorType(Struct):
    logs_groups: list[LogGroupByErrorType]
    total_count: int
