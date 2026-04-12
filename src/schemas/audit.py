# src/schemas/audit.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict
import uuid

class AuditSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    method: str
    path: str
    status_code: int
    user_id: str | None
    latency_ms: int
    ip: str | None
    is_suspicious: bool
    created_at: datetime
