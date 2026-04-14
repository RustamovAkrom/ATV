from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import get_db_engine, get_session_factory
from core.requests import get_http_transport
from core.config import get_settings
from scripts.bootstrap.rbac import seed_rbac


async def run_bootstrap():
    session_factory = get_session_factory()
    async with session_factory() as session:
        async with session.begin():
            await seed_rbac(session)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    db_engine = get_db_engine()
    http_transport = get_http_transport()

    # if settings.ENV in ("local", "dev"):
    #     await run_bootstrap()

    yield
    await db_engine.dispose()
    await http_transport.aclose()
