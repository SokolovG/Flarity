from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.infrastructure.settings.llm_provider_settings import LLMProviderSettings
from src.infrastructure.settings.llm_settings import LLMSettings
from src.infrastructure.settings.log_source_settings import LogsSourceSettings
from src.infrastructure.settings.notification_settings import NotificationSettings
from src.infrastructure.settings.report_settings import ReportSettings
from src.infrastructure.settings.storage_settings import StorageSettings

PROVIDER_PREFIXES = {
    "yandex": ["YANDEX_"],
    "ollama": ["DEEPSEEK_", "QWEN", "LLAMA_", "GEMMA"],
}


# TODO: привести все к одному типу - с env_nested_delimiter или наоборот
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
    def check_llm_model_and_provider(self) -> Self:
        provider = self.llm_provider.provider
        model_name = self.llm_settings.model.name

        allowed_prefixes = PROVIDER_PREFIXES.get(provider)
        if not allowed_prefixes:
            raise ValueError(f"Unknown provider: {provider}")

        if not any(model_name.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError(
                f"Model '{self.llm_settings.model.value}' is incompatible with provider '{provider}'"
            )

        return self
