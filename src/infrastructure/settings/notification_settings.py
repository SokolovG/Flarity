from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseNotificationConfig(BaseModel):
    """Base config for all providers."""


class TelegramConfig(BaseNotificationConfig):
    bot_token: str
    chat_id: int | str | None = None


class NotificationSettings(BaseSettings):
    provider: str
    config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_prefix="NOTIFICATION_", case_sensitive=False, env_nested_delimiter="__"
    )

    @property
    def get_config(self) -> BaseNotificationConfig:
        match self.provider:
            case "telegram":
                return TelegramConfig(**self.config)
            case _:
                raise ValueError(f"Unknown notification provider: {self.provider}")
