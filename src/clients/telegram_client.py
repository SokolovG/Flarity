from http import HTTPMethod, HTTPStatus

from src.clients import HTTPClient
from src.core.settings.notification_settings import NotificationSettings
from src.exceptions.telegram_exceptions import (
    TelegramBadRequestError,
    TelegramError,
    TelegramRateLimitError,
)


class TelegramClient:
    def __init__(self, http_client: HTTPClient, settings: NotificationSettings):
        self._http = http_client
        self.settings = settings

    @property
    def _base_url(self) -> str:
        return f"https://api.telegram.org/bot{self.settings.telegram_bot_token}"

    async def send_message(
        self, text: str, parse_mode: str = "Markdown", disable_notification: bool = False
    ) -> bool:
        data = {"text": text, "parse_mode": "HTML"}
        response = await self._http.make_request(
            method=HTTPMethod.POST,
            url=f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage",
        )

        if response.status_code != HTTPStatus.OK:
            if response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                raise TelegramError("Telegram is temporarily unavailable")
            elif response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                raise TelegramError(f"Telegram server error: {response.status_code}")
            elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise TelegramRateLimitError(
                    "Rate limit exceeded", details={"status": response.status_code}
                )
            elif response.status_code >= 400:
                raise TelegramBadRequestError(f"Bad request: {response.status_code}")
        return True

        # TODO:
        # Проверить длину текста
        # Если текст длинный — разбить на части
