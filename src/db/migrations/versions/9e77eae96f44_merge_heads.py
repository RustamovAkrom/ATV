"""merge heads

Revision ID: 9e77eae96f44
Revises: 30ea20601c53, f1c2d3e4a5b6
Create Date: 2026-05-17 22:23:52.952007

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "9e77eae96f44"
down_revision: str | Sequence[str] | None = ("30ea20601c53", "f1c2d3e4a5b6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
