# src/db/models/assets/asset_category.py

from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from db.base import Base, UUIDMixing, TimestampMixin

if TYPE_CHECKING:
    from .asset import Asset
    from .asset_model import AssetModel


class AssetCategory(Base, UUIDMixing, TimestampMixin):
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
        lazy="selectin"
    )

    children: Mapped[List["AssetCategory"]] = relationship(
        "AssetCategory",
        back_populates="parent",
        lazy="selectin"
    )

    models: Mapped[List["AssetModel"]] = relationship(
        "AssetModel",
        back_populates="category",
        lazy="selectin",
    )

    # business logic
    def is_root(self) -> bool:
        return self.parent_id is None

    def get_full_path(self) -> list[str]:
        node = self
        path = []
        while node:
            path.append(node.name)
            node = node.parent
        return list(reversed(path))
