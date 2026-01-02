from datetime import datetime

from msgspec import Struct, field

from src.domain.entities.enums import LogLevel


class LogEntry(Struct):
    timestamp: datetime
    message: str
    level: LogLevel
    app: str

    metadata: dict[str, str] = field(default_factory=dict)
