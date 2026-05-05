import sys
import asyncio

sys.path.append('e:/IIB ATV/src')

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import get_settings
from app import create_app
from db.dependencies import get_db_session
from db.meta import meta
from db.models import load_all_models

async def main():
    settings = get_settings()
    load_all_models()
    engine = create_async_engine(str(settings.postgres_async_url), echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        app = create_app()

        async def override_db():
            yield session

        app.dependency_overrides[get_db_session] = override_db
        app.user_middleware = [
            m for m in app.user_middleware if m.cls.__name__ != 'AuditMiddleware'
        ]
        if hasattr(app.state, 'limiter'):
            app.state.limiter.enabled = False

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            r = await client.post('/auth/login', data={'username':'superadmin','password':'password'})
            print('login', r.status_code, r.text)

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
