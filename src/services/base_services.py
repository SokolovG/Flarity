from abc import ABC, abstractmethod
from typing import Literal, Protocol

from src.core.settings.log_source_settings import LogsSourceSettings
from src.entities.report import ReportData
from src.responses import LogsByErrorType, LogsSourceQueryResult


class LogSourceService(Protocol):
    async def get_recent_errors(self, hours: int) -> LogsSourceQueryResult: ...
    async def _group_errors_by_type(self, logs: LogsSourceQueryResult) -> LogsByErrorType: ...
    async def check_readiness(self) -> bool: ...


class BaseNotificationService(Protocol):
    async def send_message(
        self,
        message: str,
        parse_mode: Literal["HTML", "Markdown", "MarkdownV2"] = "HTML",
        chat_id: str | None = None,
    ) -> bool: ...
