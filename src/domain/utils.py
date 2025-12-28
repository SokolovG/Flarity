from src.domain.value_objects.time_range import TimeRange


def format_time_range(time_range: TimeRange) -> str:
    unit = "hour" if time_range.hours == 1 else "hours"
    return f"{time_range.hours} {unit}"
