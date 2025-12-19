from src.clients import TelegramClient
from src.core.settings.notification_settings import NotificationSettings
from src.entities.report import ReportData
from src.services.base_services import BaseNotificationService


class NotificationService(BaseNotificationService):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    async def send_message(self, message: str) -> bool:
        return await self.telegram_client.send_message(message)
