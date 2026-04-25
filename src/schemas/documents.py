from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from db.models.enums import DocumentStatus


class DocumentFileCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=500)
    file_size: int | None = Field(default=None, ge=0)
    content_type: str | None = Field(default=None, max_length=100)


class AssetDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    document_type: str = Field(default="other", min_length=1, max_length=50)
    status: DocumentStatus = DocumentStatus.DRAFT
    metadata: dict = Field(default_factory=dict)
    files: list[DocumentFileCreate] = Field(default_factory=list)


class DocumentFileSchema(BaseModel):
    id: UUID
    file_name: str
    file_path: str
    file_size: int | None
    content_type: str | None

    model_config = ConfigDict(from_attributes=True)


class AssetDocumentSchema(BaseModel):
    id: UUID
    title: str
    description: str | None
    document_type: str
    asset_id: UUID | None
    created_by_id: UUID
    status: DocumentStatus
    metadata: dict = Field(alias="meta")
    files: list[DocumentFileSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
