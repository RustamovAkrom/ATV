"""

Revision ID: bd6194cb2a03
Revises: 65527c60413c
Create Date: 2026-05-05 17:26:35.540117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bd6194cb2a03'
down_revision: Union[str, Sequence[str], None] = '65527c60413c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. создаём ENUM тип
    user_status_enum = postgresql.ENUM(
        "active",
        "blocked",
        "archived",
        name="user_status",
    )
    user_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. меняем колонку с кастом
    op.execute(
        "ALTER TABLE users ALTER COLUMN status TYPE user_status USING status::text::user_status"
    )

def downgrade() -> None:
    # 1. обратно в string
    op.execute(
        "ALTER TABLE users ALTER COLUMN status TYPE VARCHAR(50) USING status::text"
    )

    # 2. удалить enum тип
    user_status_enum = postgresql.ENUM(
        "active",
        "blocked",
        "archived",
        name="user_status",
    )
    user_status_enum.drop(op.get_bind(), checkfirst=True)
