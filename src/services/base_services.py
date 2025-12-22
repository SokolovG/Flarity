from abc import ABC, abstractmethod

from src.core.settings.log_source_settings import LogsSourceSettings
from src.entities.report import ReportData
from src.responses import LogsByErrorType, LogsSourceQueryResult


class LogSourceService(ABC):
    def __init__(self, settings: LogsSourceSettings):
        self.settings = settings

    @abstractmethod
    async def get_recent_errors(self, hours: int) -> LogsSourceQueryResult: ...
    @abstractmethod
    async def _group_errors_by_type(self, logs: LogsSourceQueryResult) -> LogsByErrorType: ...
    @abstractmethod
    async def check_readiness(self) -> bool: ...


class BaseNotificationService(ABC):
    @abstractmethod
    async def send_message(
        self, message: str, parse_mode: str = "HTML", chat_id: str | None = None
    ) -> bool: ...
