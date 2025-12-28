from typing import Any, overload

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseLogsSourceConfig(BaseModel):
    """Base config for all providers."""


class LokiConfig(BaseLogsSourceConfig):
    url: str
    app_name: str


class LogsSourceSettings(BaseSettings):
    provider: str

    config: dict[str, Any] = {}
    model_config = SettingsConfigDict(
        env_prefix="LOG_SOURCE_", case_sensitive=False, env_nested_delimiter="__"
    )

    @overload  # type: ignore[misc]
    def get_config(self, config_type: type[LokiConfig]) -> LokiConfig: ...

    def get_config(self, config_type: type[BaseLogsSourceConfig]) -> BaseLogsSourceConfig:
        if config_type == LokiConfig and self.provider != "telegram":
            raise ValueError("Provider mismatch!")

        return config_type(**self.config)
