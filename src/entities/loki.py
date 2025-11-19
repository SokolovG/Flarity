from dataclasses import dataclass
from datetime import datetime

from src.entities.enums import LogLevel


@dataclass
class LogEntry:
    """Одна запись лога"""

    timestamp: datetime
    message: str
    level: LogLevel
    app: str
