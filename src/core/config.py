import os
from functools import cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

ENV_FILE_PATH = (
    {
        "local": ".env",
        "ci": ".env.ci",
        "test": ".env.test",
    }
).get(os.getenv("ENV", "local"), ".env")


class Settings(BaseSettings):
    """
    These parameters can be configured with environment variables.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="allow",
    )

    # App core
    APP_TITLE: str = "TTM"
    APP_NAME: str = "fastapi-backend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "..."
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True

    ENV: Literal["local", "test", "ci", "dev", "prod"] = "prod"
    ROOT_PATH: str = ""

    DEBUG: bool = True
    SECRET_KEY: str

    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret(cls, v: str):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 charecters")
        return v


    # PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_ECHO: bool = True

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "iib-backend"
    JWT_AUDIENCE: str = "iib-client"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SlowAPI
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE_URL: str = "memory://"
    RATE_LIMIT_DEFAULT: str = "10/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_TRUSTED_PROXIES: str = ""

    # redis
    REDIS_URL: str
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_BLOCK_SECONDS: int = 15

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"

    # E-Mail
    SMTP_FROM: str
    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    # Sentry
    SENTRY_DSN: str | None = None

    # Prometheus
    PROMETHEUS_METRICS_KEY: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_INCLUDE_REQUEST_ID: bool = True
    SERVICE_NAME: str = "iib-backend"


    @property
    def postgres_async_url(self) -> str:
        return str(
            URL.build(
                scheme="postgresql+asyncpg",
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=f"/{self.POSTGRES_DB}",
            )
        )

    @property
    def postgres_sync_url(self) -> str:
        return str(
            URL.build(
                scheme="postgresql+psycopg",
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=f"/{self.POSTGRES_DB}",
            )
        )

@cache
def get_settings() -> Settings:
    return Settings()
