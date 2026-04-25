# src/db/models/assets/asset_category.py

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.mixins.slug_mixin import SlugMixin

if TYPE_CHECKING:
    from .asset_model import AssetModel


class AssetCategory(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "asset_categories"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)

    parent_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("asset_categories.id", ondelete="SET NULL")
    )

    # self-referential tree
    parent: Mapped[Optional["AssetCategory"]] = relationship(
        "AssetCategory",
        remote_side="AssetCategory.id",
        back_populates="children",
        lazy="selectin",
    )

    children: Mapped[List["AssetCategory"]] = relationship(
        "AssetCategory", back_populates="parent", lazy="selectin"
    )

    models: Mapped[List["AssetModel"]] = relationship(
        "AssetModel",
        back_populates="category",
        lazy="selectin",
    )
