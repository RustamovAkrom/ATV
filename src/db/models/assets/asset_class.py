from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.mixins.slug_mixin import SlugMixin

if TYPE_CHECKING:
    from .asset import Asset


class AssetClass(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "asset_classes"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    assets: Mapped[list["Asset"]] = relationship(
        "Asset", back_populates="asset_class", lazy="selectin"
    )

    __table_args__ = (
        Index("uq_asset_class_name_lower", func.lower(name), unique=True),
    )
