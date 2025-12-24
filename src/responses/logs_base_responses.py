from msgspec import Struct

from src.domain.entities.log_entry import LogEntry


class LogsSourceQueryResult(Struct):
    logs: list[LogEntry]
    total_count: int


class LogGroupByErrorType(Struct):
    error: str
    logs: list[LogEntry]
