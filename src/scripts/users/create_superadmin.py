# scripts/users/create_superadmin.py

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.errors import InternalError
from core.security.passwords import hash_password
from db.models.enums import UserRole, UserStatus
from db.models.users.permission import Role
from db.models.users.user import User
from utils.helpers import utc_now


async def create_superadmin(db: AsyncSession):
    print("=== Create SuperAdmin ===")

    # -------------------------
    # input (basic validation)
    # -------------------------
    login = input("Login: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()

    if not login or not password or not email or not phone:
        print("❌ All fields are required")
        return

    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return

    # -------------------------
    # check existing (FULL CHECK)
    # -------------------------
    existing = await db.execute(
        select(User).where(
            or_(
                User.login == login,
                User.email == email,
                User.phone == phone,
            )
        )
    )
    user = existing.scalar_one_or_none()

    if user:
        print("⚠️ User already exists (login/email/phone)")
        return user  # idempotent

    # -------------------------
    # get role
    # -------------------------
    role_result = await db.execute(
        select(Role).where(Role.code == UserRole.SUPERADMIN.value)
    )
    role = role_result.scalar_one_or_none()

    if not role:
        print("❌ Roles not initialized. Run bootstrap first.")
        return

    # -------------------------
    # create user
    # -------------------------
    user = User(
        login=login,
        password_hash=hash_password(password),
        email=email,
        phone=phone,
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
        created_at=utc_now(),
        updated_at=utc_now(),
    )

    db.add(user)

    # -------------------------
    # safe commit
    # -------------------------
    try:
        await db.flush()  # быстрее чем commit, ловит ошибки

    except IntegrityError:
        # race condition safe
        await db.rollback()
        print("⚠️ User already exists (race condition)")
        return

    except Exception as e:
        await db.rollback()
        print(f"❌ Unexpected error: {e}")
        raise InternalError()

    print("✅ SuperAdmin created successfully")
    return user
