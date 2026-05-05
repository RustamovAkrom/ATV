from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from db.models.enums import TransferStatus


class AssetTransferCreate(BaseModel):
    to_warehouse_id: UUID | None = None
    to_service_id: UUID | None = None
    comment: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_destination(self):
        if self.to_warehouse_id is None and self.to_service_id is None:
            raise ValueError("Transfer requires a target warehouse or service")
        return self


class AssetTransferDecision(BaseModel):
    comment: str | None = Field(default=None, max_length=255)


class AssetTransferSchema(BaseModel):
    id: UUID
    asset_id: UUID
    created_by_id: UUID
    received_by_id: UUID | None
    status: TransferStatus
    from_warehouse_id: UUID | None
    to_warehouse_id: UUID | None
    from_service_id: UUID | None
    to_service_id: UUID | None
    comment: str | None
    transferred_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
