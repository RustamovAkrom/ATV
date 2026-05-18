# src/db/models/documents/document_file.py

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import UUIDMixing

if TYPE_CHECKING:
    from db.models.documents.document import Document


class DocumentFile(Base, UUIDMixing):
    __tablename__ = "document_files"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="files", lazy="selectin")

    def __repr__(self):
        return f"{self.file_name} | SIZE: {self.file_size}"
