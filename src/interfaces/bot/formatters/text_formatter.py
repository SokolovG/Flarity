from src.domain.entities.enums import LLMModel
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.settings.app_settings import AppSettings


class BotTextFormatter:
    @staticmethod
    def format_settings(app_settings: AppSettings) -> str:
        info = f"""
Current config:
• LLM provider: {app_settings.llm_provider.provider.capitalize()}
• LLM model: {app_settings.llm.model.value.capitalize()}
• Storage provider: {app_settings.storage.provider.capitalize()}
• Logs source provider: {app_settings.log_source.provider.capitalize()}
{(f"• Schedule: every {TimeRange(int(app_settings.schedule_interval_hours)).hour_and_unit}") if app_settings.schedule_enabled else ""}
            """
        return info

    @staticmethod
    def format_help() -> str:
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
