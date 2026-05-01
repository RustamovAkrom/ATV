from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import NotFound
from db.models.documents.document import Document
from db.models.documents.document_file import DocumentFile
from repositories.documents.document_repo import DocumentRepository
from schemas.documents import AssetDocumentCreate, AssetDocumentSchema
from utils.helpers import utc_now
from schemas.auth.auth import CurrentUserSchema
from core.events.document_events import DocumentEventService


class DocumentService:
    def __init__(
        self,
        repo: DocumentRepository,
        events: DocumentEventService,
    ):
        self.repo = repo
        self.events = events

    async def attach_document_to_asset(
        self, asset_id: UUID, data: AssetDocumentCreate, actor: CurrentUserSchema
    ) -> AssetDocumentSchema:

        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        document = Document(
            title=data.title.strip(),
            description=(data.description or "").strip() or None,
            document_type=data.document_type.strip(),
            asset_id=asset.id,
            created_by_id=actor.id,
            status=data.status,
            meta=data.metadata,
            files=[
                DocumentFile(
                    file_name=file.file_name.strip(),
                    file_path=file.file_path.strip(),
                    file_size=file.file_size,
                    content_type=(file.content_type or "").strip() or None,
                )
                for file in data.files
            ],
        )

        await self.repo.create_document(document)

        # ✅ ЕДИНЫЙ EVENT
        await self.events.attached(
            asset_id=asset.id,
            document_id=document.id,
            actor_id=actor.id,
        )

        return AssetDocumentSchema.model_validate(document, from_attributes=True)

    async def delete_document(
        self, asset_id: UUID, document_id: UUID, actor: CurrentUserSchema
    ) -> None:

        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset.id:
            raise NotFound("Document not found")

        await self.repo.delete_document(document)

        await self.events.deleted(
            asset_id=asset.id,
            document_id=document.id,
            actor_id=actor.id,
        )

    async def list_by_asset(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> list[AssetDocumentSchema]:

        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        documents = await self.repo.list_documents_by_asset(asset_id)

        return [
            AssetDocumentSchema.model_validate(document, from_attributes=True)
            for document in documents
        ]
