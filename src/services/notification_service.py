from src.clients import TelegramClient
from src.core.settings.notification_settings import NotificationSettings
from src.entities.report import ReportData
from src.services.base_services import BaseNotificationService
from src.services.report_formatter_service import ReportFormatter


class NotificationService(BaseNotificationService):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    async def send_analysis_report(self, report_data: ReportData) -> bool:
        report = ReportFormatter.to_html(data=report_data)
        return await self.telegram_client.send_message(report)
