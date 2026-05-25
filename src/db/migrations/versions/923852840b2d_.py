"""
Revision ID: 923852840b2d
Revises: b122b9d74fad
Create Date: 2026-05-12 02:25:47.286627

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "923852840b2d"
down_revision: str | Sequence[str] | None = "b122b9d74fad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # ========== 1. СНАЧАЛА СОЗДАЕМ ENUM ТИПЫ ==========
    # Создаем ENUM для employment_type
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'employment_type') THEN
                CREATE TYPE employment_type AS ENUM ('FULL_TIME', 'PART_TIME', 'CONTRACTOR', 'INTERN');
            END IF;
        END $$;
    """)

    # Создаем ENUM для gender
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender') THEN
                CREATE TYPE gender AS ENUM ('MALE', 'FEMALE');
            END IF;
        END $$;
    """)

    # Создаем ENUM для user_language
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_language') THEN
                CREATE TYPE user_language AS ENUM ('RU', 'UZ', 'EN');
            END IF;
        END $$;
    """)

    # ========== 2. ТЕПЕРЬ ДОБАВЛЯЕМ КОЛОНКИ ==========
    op.add_column(
        "users",
        sa.Column(
            "department",
            sa.String(length=255),
            nullable=True,
            comment="Department/division",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "employment_type",
            sa.Enum(
                "FULL_TIME", "PART_TIME", "CONTRACTOR", "INTERN", name="employment_type"
            ),
            nullable=True,
            comment="Type of employment",
        ),
    )

    op.add_column(
        "users",
        sa.Column("date_of_birth", sa.Date(), nullable=True, comment="Date of birth"),
    )

    op.add_column(
        "users",
        sa.Column(
            "gender",
            sa.Enum("MALE", "FEMALE", name="gender"),
            nullable=True,
            comment="Gender",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "avatar_url",
            sa.String(length=500),
            nullable=True,
            comment="URL user avatar",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "avatar_thumbnail_url",
            sa.String(length=500),
            nullable=True,
            comment="URL miniature avatar",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "language",
            sa.Enum("RU", "UZ", "EN", name="user_language"),
            nullable=False,
            server_default="RU",
            comment="Interface language",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "timezone",
            sa.String(length=50),
            nullable=True,
            server_default="Asia/Tashkent",
            comment="Timezone (IANA)",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "theme_preference",
            sa.String(length=20),
            nullable=True,
            server_default="light",
            comment="Theme preference",
        ),
    )

    # ========== 3. ОБНОВЛЯЕМ КОММЕНТАРИИ ==========
    op.alter_column(
        "users",
        "badge_number",
        existing_type=sa.VARCHAR(length=50),
        comment="Employee badge number",
        existing_nullable=True,
    )

    op.alter_column(
        "users",
        "passport_number",
        existing_type=sa.VARCHAR(length=50),
        comment="Passport number",
        existing_nullable=True,
    )

    # ========== 4. СОЗДАЕМ ИНДЕКСЫ ==========
    op.create_index("idx_users_department", "users", ["department"])
    op.create_index("idx_users_employment_type", "users", ["employment_type"])
    op.create_index("idx_users_language", "users", ["language"])
    op.create_index("idx_users_date_of_birth", "users", ["date_of_birth"])


def downgrade() -> None:
    """Downgrade schema."""

    # ========== 1. УДАЛЯЕМ ИНДЕКСЫ ==========
    op.drop_index("idx_users_date_of_birth", table_name="users")
    op.drop_index("idx_users_language", table_name="users")
    op.drop_index("idx_users_employment_type", table_name="users")
    op.drop_index("idx_users_department", table_name="users")

    # ========== 2. ВОЗВРАЩАЕМ КОММЕНТАРИИ ==========
    op.alter_column(
        "users",
        "passport_number",
        existing_type=sa.VARCHAR(length=50),
        comment=None,
        existing_comment="Passport number",
        existing_nullable=True,
    )

    op.alter_column(
        "users",
        "badge_number",
        existing_type=sa.VARCHAR(length=50),
        comment=None,
        existing_comment="Employee badge number",
        existing_nullable=True,
    )

    # ========== 3. УДАЛЯЕМ КОЛОНКИ ==========
    op.drop_column("users", "theme_preference")
    op.drop_column("users", "timezone")
    op.drop_column("users", "language")
    op.drop_column("users", "avatar_thumbnail_url")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "gender")
    op.drop_column("users", "date_of_birth")
    op.drop_column("users", "employment_type")
    op.drop_column("users", "department")

    # ========== 4. УДАЛЯЕМ ENUM ТИПЫ (ОСТОРОЖНО!) ==========
    # Проверяем, не используются ли типы в других таблицах
    op.execute("""
        DO $$
        BEGIN
            -- Удаляем только если тип существует и не используется
            IF EXISTS (
                SELECT 1 FROM pg_type
                WHERE typname = 'user_language'
                AND NOT EXISTS (
                    SELECT 1 FROM pg_attribute
                    WHERE atttypid = (SELECT oid FROM pg_type WHERE typname = 'user_language')
                )
            ) THEN
                DROP TYPE user_language;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type
                WHERE typname = 'gender'
                AND NOT EXISTS (
                    SELECT 1 FROM pg_attribute
                    WHERE atttypid = (SELECT oid FROM pg_type WHERE typname = 'gender')
                )
            ) THEN
                DROP TYPE gender;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type
                WHERE typname = 'employment_type'
                AND NOT EXISTS (
                    SELECT 1 FROM pg_attribute
                    WHERE atttypid = (SELECT oid FROM pg_type WHERE typname = 'employment_type')
                )
            ) THEN
                DROP TYPE employment_type;
            END IF;
        END $$;
    """)
