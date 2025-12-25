from datetime import datetime

from msgspec import Struct

from src.domain.entities.enums import LogLevel


class LogEntry(Struct):
    timestamp: datetime
    message: str
    level: LogLevel
    app: str

    metadata: dict[str, str] = {}
