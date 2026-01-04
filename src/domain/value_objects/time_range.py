from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar


@dataclass(frozen=True)
class TimeRange:
    hours: int = field()
    MAX_HOURS: ClassVar[int] = 168

    def to_timestamps(self, current_time: datetime) -> tuple[datetime, datetime]:
        end = current_time
        start = end - timedelta(hours=self.hours)
        return start, end

    @property
    def hour_and_unit(self) -> str:
        unit = "hour" if self.hours == 1 else "hours"
        return f"{self.hours} {unit}"

    def __post_init__(self) -> None:
        if not 1 <= self.hours <= self.MAX_HOURS:
            raise ValueError(f"Hours must be between 1 and {self.MAX_HOURS}")
