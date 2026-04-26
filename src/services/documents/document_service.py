from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import NotFound
from db.models.documents.document import Document
from db.models.documents.document_file import DocumentFile
from repositories.documents.document_repo import DocumentRepository
from schemas.documents import AssetDocumentCreate, AssetDocumentSchema
from utils.helpers import utc_now


class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def attach_document_to_asset(
        self, asset_id: UUID, data: AssetDocumentCreate, actor_id: UUID
    ) -> AssetDocumentSchema:
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        document = Document(
            title=data.title.strip(),
            description=(data.description or "").strip() or None,
            document_type=data.document_type.strip(),
            asset_id=asset.id,
            created_by_id=actor_id,
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
        await self.repo.add_history(
            asset.id, actor_id, "document_attached", f"Document {document.id} attached"
        )
        await self._publish(
            "asset.document_attached",
            {
                "asset_id": str(asset.id),
                "document_id": str(document.id),
                "actor_id": str(actor_id),
            },
        )
        return AssetDocumentSchema.model_validate(document, from_attributes=True)

    async def delete_document(
        self, asset_id: UUID, document_id: UUID, actor_id: UUID
    ) -> None:
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        document = await self.repo.get_document(document_id)
        if not document or document.asset_id != asset.id:
            raise NotFound("Document not found")

        await self.repo.add_history(
            asset.id, actor_id, "document_deleted", f"Document {document.id} deleted"
        )
        await self._publish(
            "asset.document_deleted",
            {
                "asset_id": str(asset.id),
                "document_id": str(document.id),
                "actor_id": str(actor_id),
            },
        )
        await self.repo.delete_document(document)

    async def _publish(self, event: str, payload: dict) -> None:
        try:
            await audit_stream.publish(
                {"event": event, **payload, "timestamp": utc_now().timestamp()}
            )
        except Exception:
            return
