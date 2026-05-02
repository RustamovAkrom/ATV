from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, UUIDMixin, TimestampMixin


class AssetHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "asset_history"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    action: Mapped[str] = mapped_column(
        String(50)
    )  # "status_change", "repair_finished", "assigned"
    description: Mapped[str] = mapped_column(Text)

    asset = relationship("Asset", back_populates="history_entries", lazy="selectin")
    user = relationship("User", lazy="selectin")
