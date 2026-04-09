import os
from functools import cache
from typing import Literal

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv
from yarl import URL

load_dotenv()

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
    APP_NAME: str = "fastapibackend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "..."
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True

    ENV: Literal["local", "test", "ci", "dev", "prod"] = "prod"
    ROOT_PATH: str = ""

    DEBUG: bool = True
    SECRET_KEY: str
    SERVICE_NAME: str = "fastapi-backend"

    # PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_ECHO: bool = True

    # JWT
    # JWT_SECRET_KEY: str
    # JWT_ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRES_MINUTES: int = 15
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 7

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
