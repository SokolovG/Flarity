from typing import Any, overload

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

    @overload  # type: ignore[misc]
    def get_config(self, config_type: type[TelegramConfig]) -> TelegramConfig: ...

    def get_config(self, config_type: type[BaseNotificationConfig]) -> BaseNotificationConfig:
        if config_type == TelegramConfig and self.provider != "telegram":
            raise ValueError("Provider mismatch!")

        return config_type(**self.config)
