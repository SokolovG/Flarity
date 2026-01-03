from typing import Any, overload

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.enums import NotificationProvider


class BaseNotificationConfig(BaseModel):
    """Base config for all providers."""


class TelegramConfig(BaseNotificationConfig):
    bot_token: str
    chat_id: int | str | None = None


class NotificationSettings(BaseSettings):
    provider: NotificationProvider
    config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_prefix="NOTIFICATION_", case_sensitive=False, env_nested_delimiter="__"
    )

    @overload  # type: ignore[misc]
    def get_config(self, config_type: type[TelegramConfig]) -> TelegramConfig: ...

    def get_config(self, config_type: type[BaseNotificationConfig]) -> BaseNotificationConfig:
        if config_type == TelegramConfig and self.provider != NotificationProvider.TELEGRAM:
            raise ValueError("Notifcation provider mismatch!")

        return config_type(**self.config)
