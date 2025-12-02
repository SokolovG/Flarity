from abc import ABC, abstractmethod

from src.core.app_settings import Settings
from src.responses import LogsByErrorType, LogsSourceQueryResult


class LogSourceService(ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    async def get_recent_errors(self, hours: int = 24) -> LogsSourceQueryResult: ...
    @abstractmethod
    async def group_errors_by_type(self, logs: LogsSourceQueryResult) -> LogsByErrorType: ...
    @abstractmethod
    async def check_readiness(self) -> bool: ...
