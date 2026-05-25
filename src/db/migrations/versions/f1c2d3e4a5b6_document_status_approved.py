"""

Revision ID: f1c2d3e4a5b6
Revises: e435e08b9d03
Create Date: 2026-05-17 15:20:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1c2d3e4a5b6"
down_revision: str | Sequence[str] | None = "e435e08b9d03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'documentstatus'
                  AND e.enumlabel = 'archived'
            ) THEN
                ALTER TYPE documentstatus RENAME VALUE 'archived' TO 'approved';
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'documentstatus'
                  AND e.enumlabel = 'approved'
            ) THEN
                ALTER TYPE documentstatus RENAME VALUE 'approved' TO 'archived';
            END IF;
        END
        $$;
        """
    )
