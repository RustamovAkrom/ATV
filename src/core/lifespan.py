import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.database.db_async import get_async_session_factory, get_db_async_engine
from core.requests import get_http_transport
from scripts.bootstrap.rbac import seed_rbac


async def run_bootstrap():
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        async with session.begin():
            await seed_rbac(session)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_engine = get_db_async_engine()
    http_transport = get_http_transport()
    # await run_bootstrap()
    yield
    await db_engine.dispose()
    await http_transport.aclose()
