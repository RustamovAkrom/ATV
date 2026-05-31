from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db.models.assets.asset import Asset
from db.models.documents.document import Document
from db.models.documents.document_file import DocumentFile
from repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_asset(self, asset_id: UUID) -> list[Document]:
        """Список документов по активу"""
        result = await self.session.execute(
            select(Document)
            .options(
                selectinload(Document.files),
                joinedload(Document.created_by),
            )
            .where(Document.asset_id == asset_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.unique().scalars().all())

    async def get_document(self, document_id: UUID) -> Document | None:
        """Получить документ по ID"""
        result = await self.session.execute(
            select(Document)
            .options(
                selectinload(Document.files),
                joinedload(Document.created_by),
            )
            .where(Document.id == document_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        """Получить актив по ID"""
        result = await self.session.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()

    async def create_document(self, document: Document) -> Document:
        """Создать документ"""
        self.add(document)
        await self.flush()
        await self.refresh(document)
        return document

    async def update_document(self, document_id: UUID, data: dict) -> Document | None:
        """Обновить документ"""
        document = await self.get_document(document_id)
        if not document:
            return None

        for key, value in data.items():
            if value is not None:
                setattr(document, key, value)

        await self.flush()
        await self.refresh(document)
        return document

    async def delete_document(self, document: Document) -> None:
        """Удалить документ (каскадно удаляет файлы)"""
        await self.session.delete(document)
        await self.flush()

    async def get_document_file(self, file_id: UUID) -> DocumentFile | None:
        """Получить файл документа по ID"""
        result = await self.session.execute(
            select(DocumentFile).where(DocumentFile.id == file_id)
        )
        return result.scalar_one_or_none()

    async def add_file(self, document: Document, file_data: dict) -> DocumentFile:
        """Добавить файл к документу"""
        file = DocumentFile(
            document_id=document.id,
            file_name=file_data["file_name"],
            file_path=file_data["file_path"],
            file_size=file_data.get("file_size"),
            content_type=file_data.get("content_type"),
        )
        self.add(file)
        await self.flush()
        await self.refresh(file)
        return file

    async def delete_file(self, file_id: UUID) -> bool:
        """Удалить файл"""
        result = await self.session.execute(
            delete(DocumentFile).where(DocumentFile.id == file_id)
        )
        await self.flush()
        return self._rowcount(result) > 0

    async def get_document_stats(self, asset_id: UUID) -> dict:
        """Статистика по документам актива"""
        result = await self.session.execute(
            select(
                func.count(Document.id).label("total"),
                func.sum(DocumentFile.file_size).label("total_size"),
            )
            .outerjoin(DocumentFile, DocumentFile.document_id == Document.id)
            .where(Document.asset_id == asset_id)
        )
        row = result.one()
        return {
            "total_documents": row.total or 0,
            "total_files_size": row.total_size or 0,
        }
