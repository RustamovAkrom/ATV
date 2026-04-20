import asyncio

from core.database.db_async import get_async_session_factory
from core.celery import celery_app
from repositories.audit_repo import AuditRepository
from schemas.audit import AuditCreate
from services.audit_service import AuditService


@celery_app.task(bind=True, max_retries=3)
def process_audit_log_task(self, payload: dict):
    async def _run():
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            async with session.begin():
                service = AuditService(AuditRepository(session))
                await service.persist_audit(AuditCreate(**payload))

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
