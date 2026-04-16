from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class SessionOut(BaseModel):
    id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_id: Optional[str]

    is_revoked: bool
    is_active: bool

    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
