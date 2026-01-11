from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.settings.app_settings import AppSettings


class BotTextFormatter:
    @staticmethod
    def format_settings(app_settings: AppSettings) -> str:
        llm_model = app_settings.llm_settings.model
        llm_provider = app_settings.llm_provider.provider
        storage_provider = (
            app_settings.storage.provider if app_settings.storage.provider else "In memory"  # type: ignore[union-attr]
        )
        log_source_provider = app_settings.log_source.provider

        info = f"""
Current config:
- LLM provider: {llm_provider.capitalize()}
- LLM model: {llm_model.value}
- Storage provider: {storage_provider.capitalize()}
- Logs source provider: {log_source_provider.capitalize()}
{f"• Schedule: every {TimeRange(int(app_settings.schedule_interval_hours)).hour_and_unit}" if app_settings.schedule_enabled else ""}
"""
        return info.strip()

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

/bug - Report a bug

/help - This help message
                """
        return help_text
