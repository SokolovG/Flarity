from typing import Any, Literal, overload

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.enums import ReportTemplate, ReportType

# ============================================================================
# STORAGE
# ============================================================================


class BaseStorageConfig(BaseModel):
    """Base config for all storages."""


class RedisConfig(BaseStorageConfig):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None


class MemoryConfig(BaseStorageConfig):
    pass


class StorageSettings(BaseSettings):
    provider: Literal["redis", "memory"] = "memory"

    config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_prefix="STORAGE_", case_sensitive=False, env_nested_delimiter="__"
    )

    @overload
    def get_config(self, config_type: type[RedisConfig]) -> RedisConfig: ...
    @overload
    def get_config(self, config_type: type[MemoryConfig]) -> MemoryConfig: ...

    def get_config(self, config_type: type[BaseStorageConfig]) -> BaseStorageConfig:
        if config_type == RedisConfig and self.provider != "redis":
            raise ValueError("Provider mismatch!")

        return config_type(**self.config)


# ============================================================================
# REPORTS
# ============================================================================


class ReportSettings(BaseSettings):
    analyze_template: str = ReportTemplate.ANALYSIS_DETAILED.value
    recent_template: str = ReportTemplate.RECENT_ERRORS.value
    stats_template: str = ReportTemplate.STATISTICS.value

    model_config = SettingsConfigDict(env_prefix="REPORT_", case_sensitive=False)

    def get_template(self, report_type: ReportType) -> str:
        match report_type:
            case ReportType.ANALYZE:
                return self.analyze_template
            case ReportType.RECENT:
                return self.recent_template
            case ReportType.STATS:
                return self.stats_template
            case ReportType.ANSWER:
                return ReportTemplate.ANSWER.value
            case _:
                raise ValueError("Unknown template")
