from typing import Any, Literal, overload

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


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
