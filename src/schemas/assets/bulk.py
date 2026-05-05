from uuid import UUID

from pydantic import BaseModel, Field

from db.models.enums import AssetStatus
from schemas.assets.asset_transfers import AssetTransferCreate


class BulkAssignRequest(BaseModel):
    asset_ids: list[UUID] = Field(min_length=1, max_length=100)
    user_id: UUID
    atomic: bool = False


class BulkTransferRequest(BaseModel):
    asset_ids: list[UUID] = Field(min_length=1, max_length=100)
    transfer: AssetTransferCreate
    atomic: bool = False


class BulkStatusRequest(BaseModel):
    asset_ids: list[UUID] = Field(min_length=1, max_length=100)
    status: AssetStatus
    atomic: bool = False


class BulkFailedItem(BaseModel):
    id: UUID
    error: str


class BulkResult(BaseModel):
    success: list[UUID]
    failed: list[BulkFailedItem]
