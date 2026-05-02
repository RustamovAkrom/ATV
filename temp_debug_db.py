import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import get_settings
from db.models import load_all_models
from db.meta import meta

async def run():
    settings = get_settings()
    load_all_models()
    engine = create_async_engine(str(settings.postgres_async_url), echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        from db.models.documents.document import Document
        from db.models.documents.document_file import DocumentFile
        from db.models.assets.asset import Asset
        from sqlalchemy import select, func
        from uuid import uuid4
        print('connected', session)
        asset = Asset(id=uuid4(), name='TestAsset', status='active')
        session.add(asset)
        await session.flush()
        document = Document(id=uuid4(), title='Warranty', document_type='warranty', asset_id=asset.id, created_by_id=uuid4(), status='draft', meta={}, files=[DocumentFile(id=uuid4(), file_name='warranty.pdf', file_path='/tmp/warranty.pdf', file_size=1024)])
        session.add(document)
        await session.flush()
        count1 = await session.scalar(select(func.count()).select_from(Document))
        print('before delete', count1)
        session.delete(document)
        await session.flush()
        count2 = await session.scalar(select(func.count()).select_from(Document))
        print('after delete', count2)
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(run())
