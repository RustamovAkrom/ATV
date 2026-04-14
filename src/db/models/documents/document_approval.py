# src/db/models/documents/document_approval.py

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, UUIDMixing
from db.models.enums import ApprovalStatus

if TYPE_CHECKING:
    pass


class DocumentApproval(Base, UUIDMixing):
    __tablename__ = "document_approvals"
    __table_args__ = (
        UniqueConstraint("document_id", "approver_id", name="uq_document_approvals_document_approver"),
    )

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )

    approver_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(ApprovalStatus),
        default=ApprovalStatus.PENDING
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    document = relationship("Document", back_populates="approvals")
    approver = relationship("User")

    # business
    def approve(self):
        self.status = ApprovalStatus.APPROVED
        self.approved_at = datetime.utcnow()

    def reject(self):
        self.status = ApprovalStatus.REJECTED
