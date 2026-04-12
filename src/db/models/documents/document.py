# src/db/models/documents/document.py

from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    ForeignKey,
    Enum as SAEnum,
    JSON
)

from db.base import Base, UUIDMixing, TimestampMixin
from db.models.enums import DocumentStatus

if TYPE_CHECKING:
    from db.models.users.user import User
    from .document_file import DocumentFile
    from .document_approval import DocumentApproval
    from .document_signature import DocumentSignature


class Document(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))

    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus),
        default=DocumentStatus.DRAFT,
        nullable=False
    )

    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # ======================
    # RELATIONSHIPS
    # ======================

    created_by = relationship("User", lazy="selectin")

    files: Mapped[List["DocumentFile"]] = relationship(
        "DocumentFile",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    approvals: Mapped[List["DocumentApproval"]] = relationship(
        "DocumentApproval",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    signatures: Mapped[List["DocumentSignature"]] = relationship(
        "DocumentSignature",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # ======================
    # BUSINESS LOGIC
    # ======================

    def submit(self):
        if self.status != DocumentStatus.DRAFT:
            raise ValueError("Only draft can be submitted")

        self.status = DocumentStatus.PENDING

    def approve(self):
        self.status = DocumentStatus.APPROVED

    def reject(self):
        self.status = DocumentStatus.REJECTED
