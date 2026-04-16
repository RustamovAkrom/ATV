# src/db/models/documents/document_signature.py

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base, UUIDMixing

if TYPE_CHECKING:
    pass


class DocumentSignature(Base, UUIDMixing):
    __tablename__ = "document_signatures"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    signed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    document = relationship("Document", back_populates="signatures")
    user = relationship("User")
