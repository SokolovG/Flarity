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
        msg = self.message.lower()

        if "database" in msg or "postgres" in msg:
            return "DB"
        if "api" in msg or "http" in msg:
            return "API"
        if "auth" in msg or "jwt" in msg:
            return "AUTH"

        return "GENERIC"
