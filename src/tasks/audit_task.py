import asyncio

from core.celery import celery_app
from core.database.db_sync import get_sync_session_factory
from repositories.audit.audit_repo import AuditRepository
from schemas.audit import AuditCreateSchema
from services.audit.audit_service import AuditService


@celery_app.task(bind=True, max_retries=3)
def process_audit_log_task(self, payload: dict):
    try:
        session_factory = get_sync_session_factory()
        with session_factory() as session:
            with session.begin():
                service = AuditService(AuditRepository(session))
                service.persist_audit(AuditCreateSchema(**payload))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5) from exec
