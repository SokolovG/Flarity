import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeRange:
    hours: int

    def to_timestamps(self) -> tuple[datetime.datetime, datetime.datetime]:
        end = datetime.now()
        start = end - datetime.timedelta(hours=self.hours)
        return start, end

    def __post_init__(self) -> None:
        if self.hours <= 0:
            raise ValueError("Hours must be positive")
