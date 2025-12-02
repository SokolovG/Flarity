from src.clients import HTTPClient
from src.core.settings import Settings


class TelegramClient:
    def __init__(self, http_client: HTTPClient, settings: Settings):
        self._http = http_client
        self.settings = settings

    @property
    def _base_url(self) -> str:
        return f"https://api.telegram.org/bot{self.settings.TELEGRAM_BOT_TOKEN}"

    async def send_message(
        self, text: str, parse_mode: str = "Markdown", disable_notification: bool = False
    ) -> bool:
        # TODO:
        # Проверить длину текста
        # Если текст длинный — разбить на части
        return True
