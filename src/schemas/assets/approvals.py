from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from db.models.enums import ApprovalStatus
from schemas.assets.repairs import RepairPartCreate


class ApprovalCreate(BaseModel):
    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: UUID
    action: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


class ApprovalDecision(BaseModel):
    comment: str | None = Field(default=None, max_length=500)


class ApprovalSchema(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    payload: dict
    status: ApprovalStatus
    created_by_id: UUID
    approved_by_id: UUID | None
    executed: bool
    created_at: datetime
    decided_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AssetTransferApprovalPayload(BaseModel):
    to_warehouse_id: UUID | None = None
    to_service_id: UUID | None = None
    comment: str | None = Field(default=None, max_length=255)


class AssetArchiveApprovalPayload(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class AssetDeleteApprovalPayload(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class RepairCompleteApprovalPayload(BaseModel):
    repair_id: UUID
    labor_cost: Decimal | None = None
    parts: list[RepairPartCreate] = Field(default_factory=list)
