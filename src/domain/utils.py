from src.domain.entities.enums import LLMModel
from src.domain.value_objects.time_range import TimeRange


def format_time_range(time_range: TimeRange) -> str:
    unit = "hour" if time_range.hours == 1 else "hours"
    return unit
