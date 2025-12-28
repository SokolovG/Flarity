from pydantic import Field
from pydantic_settings import BaseSettings

from src.infrastructure.settings.llm_provider_settings import LLMProviderSettings
from src.infrastructure.settings.llm_settings import LLMSettings
from src.infrastructure.settings.log_source_settings import LogsSourceSettings
from src.infrastructure.settings.notification_settings import NotificationSettings
from src.infrastructure.settings.report_settings import ReportSettings
from src.infrastructure.settings.storage_settings import StorageSettings


# TODO:  добавить валидацию совместимости LLM_PROVIDER + LLM_MODEL
# TODO: привести все к одному типу - с env_nested_delimiter или наоборот
class AppSettings(BaseSettings):
    log_source: LogsSourceSettings = Field(default_factory=LogsSourceSettings)  # type: ignore[arg-type]
    llm: LLMSettings = Field(default_factory=LLMSettings)  # type: ignore[arg-type]
    llm_provider: LLMProviderSettings = Field(default_factory=LLMProviderSettings)  # type: ignore[arg-type]
    notification: NotificationSettings = Field(default_factory=NotificationSettings)  # type: ignore[arg-type]
    report: ReportSettings = Field(default_factory=ReportSettings)
    storage: StorageSettings | None = Field(default_factory=StorageSettings)
    schedule_interval_hours: str = "6"
    schedule_enabled: bool
