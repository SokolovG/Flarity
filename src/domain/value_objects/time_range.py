from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class TimeRange:
    hours: int

    def to_timestamps(self) -> tuple[datetime, datetime]:
        end = datetime.now()
        start = end - timedelta(hours=self.hours)
        return start, end

    @property
    def hour_and_unit(self) -> str:
        unit = "hour" if self.hours == 1 else "hours"
        return f"{self.hours} {unit}"

    def __post_init__(self) -> None:
        if self.hours <= 0:
            raise ValueError("Hours must be positive")
