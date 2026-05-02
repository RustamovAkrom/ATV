from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.documents.document import Document
from repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_documents_by_asset(self, asset_id: UUID) -> list[Document]:
        return await self.scalars(
            select(Document)
            .options(selectinload(Document.files))
            .where(Document.asset_id == asset_id)
        )

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        return self.scalar(
            select(Asset)
            .options(selectinload(Asset.documents).selectinload(Document.files))
            .where(Asset.id == asset_id)
        )

    async def get_document(self, document_id: UUID) -> Document | None:
        return await self.scalar(
            select(Document)
            .options(selectinload(Document.files))
            .where(Document.id == document_id)
        )

    async def create_document(self, document: Document) -> Document:
        self.add(document)
        await self.flush()
        await self.refresh(document)
        return document

    async def delete_document(self, document: Document) -> None:
        await self.delete(document)
        await self.flush()

    async def add_history(
        self, asset_id: UUID, user_id: UUID, action: str, description: str
    ) -> AssetHistory:
        entry = AssetHistory(
            asset_id=asset_id,
            user_id=user_id,
            action=action,
            description=description,
        )
        self.add(entry)
        await self.flush()
        await self.refresh(entry)
        return entry
