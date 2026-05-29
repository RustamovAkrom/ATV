from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from db.models.assets.asset import Asset


class AssetImage(Base, UUIDMixing, TimestampMixin):
    """Изображения актива (несколько на один актив)"""

    __tablename__ = "asset_images"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)

    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Связь с активом
    asset: Mapped["Asset"] = relationship(
        "Asset", back_populates="images", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_asset_images_asset_primary", "asset_id", "is_primary"),
        Index("ix_asset_images_asset_order", "asset_id", "sort_order"),
    )

    def __repr__(self):
        return f"<AssetImage {self.file_name}>"
