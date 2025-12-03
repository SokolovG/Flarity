from pydantic_settings import BaseSettings, SettingsConfigDict


class LogsSourceSettings(BaseSettings):
    url: str
    app_name: str

    model_config = SettingsConfigDict(env_prefix="LOKI_")
