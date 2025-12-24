from src.domain.entities.enums import LLMModel


def format_hours(hours: int | str) -> str:
    unit = "hour" if int(hours) == 1 else "hours"
    return unit


def get_settings_for_bot(
    provider: str, model: LLMModel, schedule_hourse: int | str, schedule_enabled: bool
) -> str:
    info = f"""
<b>Settings</b>

Current config:
• LLM provider: {provider}
• LLM model: {model}
{(f"• Schedule: every {schedule_hourse} {format_hours(schedule_hourse)}") if schedule_enabled else ""}
        """
    return info


def get_help_text_for_bot() -> str:
    help_text = """
<b>Available commands:</b>

/analyze [hours] - AI analysis of logs
Example: <code>/analyze 6</code>

/recent [hours] - Latest errors (without AI)
Example: <code>/recent 1</code>

/stats [hours] - Statistics summary
Example: <code>/stats 24</code>

/settings - Current app settings (llm and schedule)

/help - This help message
        """
    return help_text
