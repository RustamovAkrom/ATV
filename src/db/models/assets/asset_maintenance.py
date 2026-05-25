from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from db.models.users.user import User

    from .asset import Asset


class AssetMaintenance(Base, UUIDMixing, TimestampMixin):
    """Техническое обслуживание (из раздела 6 формуляра)"""

    __tablename__ = "asset_maintenances"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    performed_at: Mapped[date] = mapped_column(nullable=False)
    issues_found: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenances")
    performed_by: Mapped["User"] = relationship("User", foreign_keys=[performed_by_id])

    @validates("maintenance_type")
    def validate_type(self, key, value):
        if not value or not value.strip():
            raise ValueError("Maintenance type cannot be empty")
        return value.strip()

    def __repr__(self):
        return f"<AssetMaintenance {self.maintenance_type} at {self.performed_at}>"
