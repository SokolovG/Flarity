from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.infrastructure.settings.llm_provider_settings import LLMProviderSettings
from src.infrastructure.settings.llm_settings import LLMSettings
from src.infrastructure.settings.log_source_settings import LogsSourceSettings
from src.infrastructure.settings.notification_settings import NotificationSettings
from src.infrastructure.settings.report_settings import ReportSettings
from src.infrastructure.settings.storage_settings import StorageSettings


class AppSettings(BaseSettings):
    log_source: LogsSourceSettings = Field(default_factory=LogsSourceSettings)  # type: ignore[arg-type]
    llm_settings: LLMSettings = Field(default_factory=LLMSettings)  # type: ignore[arg-type]
    llm_provider: LLMProviderSettings = Field(default_factory=LLMProviderSettings)  # type: ignore[arg-type]
    notification: NotificationSettings = Field(default_factory=NotificationSettings)  # type: ignore[arg-type]
    report: ReportSettings = Field(default_factory=ReportSettings)
    storage: StorageSettings | None = Field(default_factory=StorageSettings)
    schedule_interval_hours: str = "6"
    schedule_enabled: bool

    @model_validator(mode="after")
    def check_compatibility(self) -> Self:
        if self.llm_settings.model.provider.value != self.llm_provider.provider:
            raise ValueError(
                f"Model {self.llm_settings.model.value} requires provider "
                f"{self.llm_settings.model.provider.value}, got {self.llm_provider.provider}"
            )
        return self
