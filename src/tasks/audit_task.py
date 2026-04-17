# src/tasks/audit_task.py

from core.celery import celery_app
from core.database.db_sync import get_sync_session_factory
from db.models.audit.audit_log import AuditLog


@celery_app.task(
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_kwargs={"max_retries": 5},
)
def process_audit_log_task(payload: dict):

    session_factory = get_sync_session_factory()
    session = session_factory()

    try:
        audit = AuditLog(**payload)
        session.add(audit)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
