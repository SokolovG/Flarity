from typing import Any

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
    model_config = SettingsConfigDict(env_prefix="LOG_SOURCE", case_sensitive=False)

    def get_config(self) -> BaseLogsSourceConfig:
        match self.provider:
            case "loki":
                return LokiConfig(**self.config)
            case _:
                raise ValueError(f"Unknown log source provider: {self.provider}")
