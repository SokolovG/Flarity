from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.infrastructure.settings.llm_provider_settings import LLMProviderSettings
from src.infrastructure.settings.llm_settings import LLMSettings
from src.infrastructure.settings.log_source_settings import LogsSourceSettings
from src.infrastructure.settings.notification_settings import NotificationSettings


class AppSettings(BaseSettings):
    log_source: LogsSourceSettings = Field(default_factory=LogsSourceSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    llm_provider: LLMProviderSettings = Field(default_factory=LLMProviderSettings)
    notification: NotificationSettings = Field(default_factory=NotificationSettings)
    schedule_interval_hours: str = "6"
    schedule_enabled: bool

    @model_validator(mode="after")
    def validate_schedule(self) -> Self:
        if self.schedule_enabled:
            try:
                hours = int(self.schedule_interval_hours)
                if hours <= 0:
                    raise ValueError("schedule_interval_hours must be positive")
            except ValueError as e:
                raise ValueError(f"Invalid schedule_interval_hours: {e}")
        return self

    @model_validator(mode="after")
    def validate_llm_provider_config(self) -> Self:
        if self.llm_provider.provider == "yandex":
            if not self.llm_provider.yandex_api_key or not self.llm_provider.yandex_catalog_id:
                raise ValueError("Yandex API key and catalog ID are required")
        elif self.llm_provider.provider == "ollama":
            if not self.llm_provider.ollama_base_url:
                raise ValueError("Ollama base URL is required")
        return self
