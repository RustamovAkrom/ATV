import os
from functools import cache
from typing import Literal
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
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

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret(cls, v: str):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 charecters")
        return v

    SERVICE_NAME: str = "iib-backend"

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
    # SlowAPI
    RATE_LIMIT_STORAGE_URL: str = "memory://"
    RATE_LIMIT_DEFAULT: str = "10/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_TRUSTED_PROXIES: str = ""
    # redis
    USE_REDIS: bool = False
    REDIS_URL: str
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_BLOCK_SECONDS: int = 15

    # Sentry
    SENTRY_DSN: str | None = None

    # Prometheus
    PROMETHEUS_METRICS_KEY: str | None = None

    @property
    def postgres_url(self) -> str:
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


@cache
def get_settings() -> Settings:
    return Settings()
