from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base, UUIDMixing


class AssetAssignment(Base, UUIDMixing):
    __tablename__ = "asset_assignments"
    __table_args__ = (
        UniqueConstraint("asset_id", "user_id"),
    )

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    unassigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    asset = relationship("Asset", lazy="selectin")
    user = relationship("User", lazy="selectin")

