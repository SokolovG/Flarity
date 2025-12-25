from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.infrastructure.settings.llm_provider_settings import LLMProviderSettings
from src.infrastructure.settings.llm_settings import LLMSettings
from src.infrastructure.settings.log_source_settings import LogsSourceSettings
from src.infrastructure.settings.notification_settings import NotificationSettings
from src.infrastructure.settings.report_settings import ReportSettings


class AppSettings(BaseSettings):
    log_source: LogsSourceSettings = Field(default_factory=LogsSourceSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    llm_provider: LLMProviderSettings = Field(default_factory=LLMProviderSettings)
    notification: NotificationSettings = Field(default_factory=NotificationSettings)
    report: ReportSettings = Field(default_factory=ReportSettings)
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
