# src/db/models/documents/document_file.py

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String

from db.base import Base, UUIDMixing

if TYPE_CHECKING:
    from .document import Document


class DocumentFile(Base, UUIDMixing):
    __tablename__ = "document_files"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))

    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    document = relationship(
        "Document",
        back_populates="files",
        lazy="selectin"
    )
