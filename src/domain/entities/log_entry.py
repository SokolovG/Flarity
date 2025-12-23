from datetime import datetime

from msgspec import Struct

from src.domain.entities.enums import LogLevel


class LogEntry(Struct):
    timestamp: datetime
    message: str
    level: LogLevel
    app: str
    target: str | None = None
    request_id: str | None = None
    method: str | None = None
    uri: str | None = None

    def get_error_category(self) -> str:
        match self.message.lower():
            case "database":
                return "DB"
            case "api":
                return "API"
            case _:
                return "GENERIC"
