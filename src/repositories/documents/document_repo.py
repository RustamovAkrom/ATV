from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.documents.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        result = await self.session.execute(
            select(Asset)
            .options(selectinload(Asset.documents).selectinload(Document.files))
            .where(Asset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def get_document(self, document_id: UUID) -> Document | None:
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.files))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def create_document(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document

    async def delete_document(self, document: Document) -> None:
        await self.session.delete(document)
        await self.session.flush()

    async def add_history(
        self, asset_id: UUID, user_id: UUID, action: str, description: str
    ) -> AssetHistory:
        entry = AssetHistory(
            asset_id=asset_id,
            user_id=user_id,
            action=action,
            description=description,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
