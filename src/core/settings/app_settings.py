from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.core.settings.llm_provider_settings import LLMProviderSettings
from src.core.settings.llm_settings import LLMSettings
from src.core.settings.log_source_serrings import LogsSourceSettings
from src.core.settings.notification_settings import NotificationSettings


class AppSettings(BaseSettings):
    log_source: LogsSourceSettings = Field(default_factory=LogsSourceSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    llm_provider: LLMProviderSettings = Field(default_factory=LLMProviderSettings)
    notification: NotificationSettings = Field(default_factory=NotificationSettings)

    @model_validator(mode="after")
    def validate_llm_provider_config(self) -> Self:
        if self.llm_provider.provider == "yandex":
            if not self.llm_provider.yandex:
                raise ValueError("Yandex config required")
        elif self.llm_provider.provider == "ollama":
            if not self.llm_provider.ollama:
                raise ValueError("Ollama config required")
        return self
