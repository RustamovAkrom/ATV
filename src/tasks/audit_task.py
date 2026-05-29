from asgiref.sync import async_to_sync

from core.celery import celery_app
from core.config import get_settings
from core.database.db_async import get_async_session_factory
from repositories.audit.audit_repo import AuditRepository
from schemas.audit import AuditCreateSchema
from services.audit.audit_service import AuditService


@celery_app.task(bind=True, max_retries=3)
def process_audit_log_task(self, payload: dict):
    if not get_settings().AUDIT_ENABLED:
        return

    async def _persist():
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            async with session.begin():
                service = AuditService(AuditRepository(session))
                await service.persist_audit(AuditCreateSchema(**payload))

    try:
        async_to_sync(_persist)()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5) from exc
