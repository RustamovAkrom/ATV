from sqlalchemy.ext.asyncio import AsyncSession
from tasks.audit_task import process_audit_log_task
from repositories.audit_repo import AuditRepository

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def create_audit_log(self, data: dict) -> None:
        audit = await self.audit_repo.create(data)

        try:
            process_audit_log_task.delay(data={
                "id": str(audit.id),
                "method": audit.method,
                "path": audit.path,
                "status_code": audit.status_code,
                "user_id": audit.user_id,
                "request_id": audit.request_id,
                "latency_ms": audit.latency_ms,
                "ip": audit.ip,
                "user_agent": audit.user_agent,
                "query": audit.query,
                "is_suspicious": audit.is_suspicious,
            })

        except Exception as e:
            pass
