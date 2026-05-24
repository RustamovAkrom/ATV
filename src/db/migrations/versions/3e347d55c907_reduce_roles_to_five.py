"""reduce_roles_to_five

Revision ID: 3e347d55c907
Revises: 4bd1671e5713
Create Date: 2026-05-22 15:29:03.014213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e347d55c907'
down_revision: Union[str, Sequence[str], None] = '4bd1671e5713'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migrate from 10 roles to 5 roles.

    Role mapping:
    - SUPERADMIN -> SUPERADMIN (keep)
    - ADMIN -> ADMIN (keep)
    - REGION_ADMIN -> ADMIN (merge)
    - REGION_MANAGER -> ADMIN (merge)
    - SERVICE_MANAGER -> ADMIN (merge)
    - MODERATOR -> OPERATOR (merge)
    - OPERATOR -> OPERATOR (keep)
    - APPROVER -> APPROVER (keep)
    - ANALYTIC -> ANALYST (rename)
    - AUDITOR -> ANALYST (merge)
    """
    # Step 1: Rename ANALYTIC to ANALYST
    op.execute("""
        UPDATE roles
        SET slug = 'analyst', name = 'Analyst'
        WHERE slug = 'analytic'
    """)

    # Step 2: Reassign users from old roles to new roles

    # MODERATOR -> OPERATOR
    op.execute("""
        UPDATE users
        SET role_id = (SELECT id FROM roles WHERE slug = 'operator')
        WHERE role_id = (SELECT id FROM roles WHERE slug = 'moderator')
    """)

    # REGION_ADMIN -> ADMIN
    op.execute("""
        UPDATE users
        SET role_id = (SELECT id FROM roles WHERE slug = 'admin')
        WHERE role_id = (SELECT id FROM roles WHERE slug = 'region_admin')
    """)

    # REGION_MANAGER -> ADMIN
    op.execute("""
        UPDATE users
        SET role_id = (SELECT id FROM roles WHERE slug = 'admin')
        WHERE role_id = (SELECT id FROM roles WHERE slug = 'region_manager')
    """)

    # SERVICE_MANAGER -> ADMIN
    op.execute("""
        UPDATE users
        SET role_id = (SELECT id FROM roles WHERE slug = 'admin')
        WHERE role_id = (SELECT id FROM roles WHERE slug = 'service_manager')
    """)

    # AUDITOR -> ANALYST
    op.execute("""
        UPDATE users
        SET role_id = (SELECT id FROM roles WHERE slug = 'analyst')
        WHERE role_id = (SELECT id FROM roles WHERE slug = 'auditor')
    """)

    # Step 3: Delete old roles from roles table
    op.execute("""
        DELETE FROM roles
        WHERE slug IN ('moderator', 'region_admin', 'region_manager', 'service_manager', 'auditor')
    """)


def downgrade() -> None:
    """
    Downgrade is not fully supported due to role merging.
    This will restore old roles but users will remain on merged roles.
    """
    # Recreate old roles (without permissions)
    op.execute("""
        INSERT INTO roles (slug, name, description) VALUES
        ('moderator', 'Moderator', 'Regional/operational management'),
        ('region_admin', 'Region Admin', 'Region-scoped admin'),
        ('region_manager', 'Region Manager', 'Region management'),
        ('service_manager', 'Service Manager', 'Service-scoped management'),
        ('auditor', 'Auditor', 'Audit and compliance focus')
        ON CONFLICT (slug) DO NOTHING
    """)

    # Rename ANALYST back to ANALYTIC
    op.execute("""
        UPDATE roles
        SET slug = 'analytic', name = 'Analytic'
        WHERE slug = 'analyst' AND id NOT IN (
            SELECT id FROM roles WHERE slug IN ('moderator', 'region_admin', 'region_manager', 'service_manager', 'auditor')
        )
    """)
