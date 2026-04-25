from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class RepairOut(BaseModel):
    id: UUID
    asset_id: UUID
    asset_name: str

    status: str
    issue: str | None

    created_at: datetime
    completed_at: datetime | None


class RepairSummaryOut(BaseModel):
    total_repairs: int
    active_repairs: int
    completed_repairs: int
