# src/db/models/documents/document.py

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.enums import DocumentStatus

if TYPE_CHECKING:
    from db.models.documents.document_file import DocumentFile


# ASSET DOCUMENT
class Document(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))

    document_type: Mapped[str] = mapped_column(String(50), index=True, default="other")

    asset_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus),
        default=DocumentStatus.DRAFT,
        nullable=False
    )

    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    created_by = relationship("User", lazy="selectin")

    files: Mapped[List["DocumentFile"]] = relationship(
        "DocumentFile",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    asset = relationship("Asset", back_populates="documents", lazy="joined")

