from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from db.models.enums import ApprovalStatus
from schemas.assets.repairs import RepairPartCreate
from schemas.base import BaseSchema


class ApprovalCreate(BaseSchema):
    """
    Schema for creating approval request.

    ⚠️ DO NOT USE DIRECTLY!
    Use specialized endpoints:
    - POST /assets/{id}/approval-requests/assignment
    - POST /assets/{id}/approval-requests/transfer
    - POST /assets/{id}/approval-requests/repair/{repair_id}/complete
    - POST /assets/{id}/approval-requests/warehouse-move
    """

    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: UUID
    action: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


class ApprovalDecision(BaseSchema):
    comment: str | None = Field(default=None, max_length=500)


class ApprovalSchema(BaseSchema):
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


class AssetTransferApprovalPayload(BaseSchema):
    to_warehouse_id: UUID | None = None
    to_service_id: UUID | None = None
    comment: str | None = Field(default=None, max_length=255)


class AssetArchiveApprovalPayload(BaseSchema):
    reason: str | None = Field(default=None, max_length=500)


class AssetDeleteApprovalPayload(BaseSchema):
    reason: str | None = Field(default=None, max_length=500)


class RepairCompleteApprovalPayload(BaseSchema):
    repair_id: UUID
    labor_cost: Decimal | None = None
    parts: list[RepairPartCreate] = Field(default_factory=list)
