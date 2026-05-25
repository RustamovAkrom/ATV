from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base
from db.mixins import UUIDMixing

if TYPE_CHECKING:
    from db.models.assets.asset import Asset
    from db.models.users.user import User


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

    asset: Mapped["Asset"] = relationship(
        "Asset", back_populates="assignments", lazy="selectin"
    )
    user: Mapped["User"] = relationship("User", lazy="selectin")

    __table_args__ = (
        Index(
            "uq_active_asset_assignment",
            "asset_id",
            unique=True,
            postgresql_where=(unassigned_at.is_(None)),
        ),
    )

    def __repr__(self):
        return f"Asset(id={self.asset_id}) assigned to User(id={self.user_id})"
