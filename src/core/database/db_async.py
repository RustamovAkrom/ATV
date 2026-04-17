from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from core.config import get_settings

@lru_cache
def get_db_async_engine() -> AsyncEngine:
    settings = get_settings()

    return create_async_engine(
        settings.postgres_async_url,
        echo=settings.POSTGRES_ECHO,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_use_lifo=True,
    )


@lru_cache
def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_db_async_engine(),
        expire_on_commit=False,
    )
