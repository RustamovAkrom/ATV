from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base, UUIDMixing


class AssetAssignment(Base, UUIDMixing):
    __tablename__ = "asset_assignments"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    asset = relationship("Asset", back_populates="assignments", lazy="selectin")
    user = relationship("User", lazy="selectin")

    __table_args__ = (
        Index(
            "uq_active_asset_assignment",
            "asset_id",
            unique=True,
            postgresql_where=(unassigned_at.is_(None)),
        ),
    )
