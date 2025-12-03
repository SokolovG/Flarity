from src.clients import TelegramClient
from src.core.settings.notification_settings import NotificationSettings
from src.responses import LLMAnalysisResult, LogsByErrorType
from src.services.base_services import BaseNotificationService


class NotificationService(BaseNotificationService):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    async def send_analysis_report(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType, time_range_hours: int = 24
    ) -> bool:
        report = self._format_report(analysis, grouped_logs, time_range_hours)
        return await self.telegram_client.send_message(report)

    def _format_report(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType, time_range_hours: int
    ) -> str:
        lines = "<b>Отчет по ошибкам за последний час</b>\n"
        return lines
