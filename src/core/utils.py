def format_hours(hours: int | str) -> str:
    unit = "hour" if int(hours) == 1 else "hours"
    return unit
