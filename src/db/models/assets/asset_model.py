from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.mixins.slug_mixin import SlugMixin

if TYPE_CHECKING:
    from .asset import Asset
    from .asset_category import AssetCategory
    from .manufacturer import Manufacturer


class AssetModel(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "asset_models"

    name: Mapped[str] = mapped_column(String(150), index=True)
    code: Mapped[str] = mapped_column(String(150), unique=True)

    manufacturer_id: Mapped[UUID] = mapped_column(
        ForeignKey("manufacturers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("asset_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    lifetime_years: Mapped[Optional[int]] = mapped_column(Integer)
    warranty_months: Mapped[Optional[int]] = mapped_column(Integer)

    manufacturer: Mapped["Manufacturer"] = relationship(
        "Manufacturer", back_populates="models", lazy="selectin"
    )
    category: Mapped["AssetCategory"] = relationship(
        "AssetCategory", back_populates="models", lazy="selectin"
    )
    assets: Mapped[List["Asset"]] = relationship(
        "Asset", back_populates="model", lazy="selectin"
    )

    @validates("lifetime_years")
    def validate_lifetime(self, key, value):
        if value is not None and value < 0:
            raise ValueError("lifetime_years must be >= 0")
        return value

    @validates("warranty_months")
    def validate_warranty(self, key, value):
        if value is not None and value < 0:
            raise ValueError("warranty_months must be >= 0")
        return value

    __table_args__ = (
        UniqueConstraint("name", "manufacturer_id", name="uq_model_manufacturer"),
        Index(
            "uq_asset_model_name_lower", func.lower(name), manufacturer_id, unique=True
        ),
    )
