from abc import ABC, abstractmethod

from src.domain.entities.log_entry import LogEntry
from src.domain.value_objects.time_range import TimeRange


class LogRepository(ABC):
    @abstractmethod
    async def get_errors(self, time_range: TimeRange) -> list[LogEntry]: ...
