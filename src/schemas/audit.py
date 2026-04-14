# src/schemas/audit.py

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    method: str
    path: str
    status_code: int
    user_id: str | None
    latency_ms: int
    ip: str | None
    user_agent: str | None
    is_suspicious: bool
    query: str | None
    created_at: datetime
