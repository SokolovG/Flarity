from datetime import datetime

from msgspec import Struct

from src.entities.enums import LogLevel


class LogEntry(Struct):
    timestamp: datetime
    message: str
    level: LogLevel
    app: str
