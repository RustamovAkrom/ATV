from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing
from db.models.enums import DocumentStatus

if TYPE_CHECKING:
    from db.models.assets.asset import Asset
    from db.models.documents.document_file import DocumentFile
    from db.models.users.user import User


# ASSET DOCUMENT
class Document(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    document_type: Mapped[str] = mapped_column(String(50), index=True, default="other")

    asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=True, index=True
    )

    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False
    )

    meta: Mapped[dict] = mapped_column(
        "meta_data",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    created_by: Mapped["User"] = relationship("User", lazy="selectin")

    files: Mapped[list["DocumentFile"]] = relationship(
        "DocumentFile",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    asset: Mapped["Asset"] = relationship(
        "Asset", back_populates="documents", lazy="joined"
    )

    def __repr__(self):
        return self.title
