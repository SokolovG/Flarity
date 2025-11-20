import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "reporty")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    LOKI_URL: str = os.getenv("LOKI_URL", "loki_url")
    LOKI_APP_NAME: str = os.getenv("LOKI_APP_NAME", "loki_app_name")


settings = Settings()
