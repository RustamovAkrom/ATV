from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.events.document import get_document_event_service
from core.events.document_events import DocumentEventService
from db.dependencies import get_db_session
from repositories.documents.document_repo import DocumentRepository
from services.documents.document_service import DocumentService


def get_document_repo(
    db: AsyncSession = Depends(get_db_session),
) -> DocumentRepository:
    return DocumentRepository(db)


def get_document_service(
    repo: DocumentRepository = Depends(get_document_repo),
    events: DocumentEventService = Depends(get_document_event_service),
) -> DocumentService:
    return DocumentService(repo, events)
