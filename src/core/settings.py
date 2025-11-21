from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOKI_URL: str
    LOKI_APP_NAME: str

    model_config = SettingsConfigDict(
        env_file="src/.env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
