# db/models/users/associations.py

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id")),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id")),
)
