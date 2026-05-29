from uuid import UUID

from core.config import get_settings
from core.events.document_events import DocumentEventService
from core.exceptions.errors import NotFound
from core.security.access_control import AccessControl
from db.models.documents.document import Document
from repositories.documents.document_repo import DocumentRepository
from schemas.auth.auth import CurrentUserSchema
from schemas.documents.document import (
    AssetDocumentCreateSchema,
    AssetDocumentOutSchema,
    AssetDocumentUpdateSchema,
    AssetDocumentWithFilesOutSchema,
    DocumentFileOutSchema,
)

settings = get_settings()


class DocumentService:
    def __init__(
        self,
        repo: DocumentRepository,
        events: DocumentEventService,
    ):
        self.repo = repo
        self.events = events

    async def list_by_asset(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> list[AssetDocumentOutSchema]:
        """Список документов актива"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        documents = await self.repo.list_by_asset(asset_id)
        return [self._to_out_schema(doc) for doc in documents]

    async def get_document(
        self, asset_id: UUID, document_id: UUID, actor: CurrentUserSchema
    ) -> AssetDocumentWithFilesOutSchema:
        """Получить документ по ID"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset_id:
            raise NotFound("Document not found")

        return self._to_with_files_schema(document)

    async def create_document(
        self,
        asset_id: UUID,
        data: AssetDocumentCreateSchema,
        actor: CurrentUserSchema,
        uploaded_files: list[dict] | None = None,
    ) -> AssetDocumentOutSchema:
        """Создать документ с файлами"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        document = Document(
            title=data.title.strip(),
            description=data.description.strip() if data.description else None,
            document_type=data.document_type.strip(),
            asset_id=asset.id,
            created_by_id=actor.id,
            status=data.status,
            meta=data.metadata,
        )

        await self.repo.create_document(document)

        # Добавляем файлы
        if uploaded_files:
            for file_data in uploaded_files:
                await self.repo.add_file(document, file_data)

        await self.events.attached(
            asset_id=asset.id,
            document_id=document.id,
            actor_id=actor.id,
            asset_name=asset.name,
        )

        return self._to_out_schema(document)

    async def update_document(
        self,
        asset_id: UUID,
        document_id: UUID,
        data: AssetDocumentUpdateSchema,
        actor: CurrentUserSchema,
    ) -> AssetDocumentOutSchema:
        """Обновить документ"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset_id:
            raise NotFound("Document not found")

        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repo.update_document(document_id, update_data)

        await self.events.updated(
            asset_id=asset.id,
            document_id=document.id,
            actor_id=actor.id,
        )

        return self._to_out_schema(updated)

    async def delete_document(
        self, asset_id: UUID, document_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Удалить документ"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset_id:
            raise NotFound("Document not found")

        await self.repo.delete_document(document)

        await self.events.deleted(
            asset_id=asset.id,
            document_id=document.id,
            actor_id=actor.id,
        )

    async def add_file_to_document(
        self,
        asset_id: UUID,
        document_id: UUID,
        file_data: dict,
        actor: CurrentUserSchema,
    ) -> DocumentFileOutSchema:
        """Добавить файл к существующему документу"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset_id:
            raise NotFound("Document not found")

        file = await self.repo.add_file(document, file_data)

        return DocumentFileOutSchema(
            id=file.id,
            file_name=file.file_name,
            file_path=file.file_path,
            file_size=file.file_size,
            content_type=file.content_type,
        )

    async def delete_file_from_document(
        self,
        asset_id: UUID,
        document_id: UUID,
        file_id: UUID,
        actor: CurrentUserSchema,
    ) -> None:
        """Удалить файл из документа"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset_id:
            raise NotFound("Document not found")

        file = await self.repo.get_document_file(file_id)
        if not file or file.document_id != document_id:
            raise NotFound("File not found")

        await self.repo.delete_file(file_id)

    def _to_out_schema(self, document: Document) -> AssetDocumentOutSchema:
        return AssetDocumentOutSchema(
            id=document.id,
            title=document.title,
            description=document.description,
            document_type=document.document_type,
            asset_id=document.asset_id,
            created_by_id=document.created_by_id,
            status=document.status,
            meta=document.meta,
            files=[
                DocumentFileOutSchema(
                    id=f.id,
                    file_name=f.file_name,
                    file_path=f.file_path,
                    file_size=f.file_size,
                    content_type=f.content_type,
                )
                for f in document.files
            ],
            created_at=document.created_at,
            updated_at=document.updated_at,
            created_by_name=(
                document.created_by.full_name if document.created_by else None
            ),
        )

    def _to_with_files_schema(
        self, document: Document
    ) -> AssetDocumentWithFilesOutSchema:
        total_size = sum(f.file_size or 0 for f in document.files)
        return AssetDocumentWithFilesOutSchema(
            id=document.id,
            title=document.title,
            description=document.description,
            document_type=document.document_type,
            asset_id=document.asset_id,
            created_by_id=document.created_by_id,
            status=document.status,
            meta=document.meta,
            files=[
                DocumentFileOutSchema(
                    id=f.id,
                    file_name=f.file_name,
                    file_path=f.file_path,
                    file_size=f.file_size,
                    content_type=f.content_type,
                )
                for f in document.files
            ],
            created_at=document.created_at,
            updated_at=document.updated_at,
            created_by_name=(
                document.created_by.full_name if document.created_by else None
            ),
            total_files_size=total_size,
            file_count=len(document.files),
        )
