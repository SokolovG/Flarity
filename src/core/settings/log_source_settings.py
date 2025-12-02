from pydantic_settings import BaseSettings, SettingsConfigDict


class LogsSourceSettings(BaseSettings):
    loki_url: str
    loki_app_name: str

    model_config = SettingsConfigDict(env_prefix="LOKI_")
