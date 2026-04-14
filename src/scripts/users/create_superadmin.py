from sqlalchemy import select

from core.security.passwords import hash_password
from db.models.enums import UserRole
from db.models.users.permission import Role
from db.models.users.user import User


async def create_superadmin(db):
    print("=== Create SuperAdmin ===")

    login = input("Login: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()

    # -------------------------
    # check exists
    # -------------------------
    existing = await db.execute(
        select(User).where(User.login == login)
    )

    if existing.scalar_one_or_none():
        print("❌ User already exists")
        return

    # -------------------------
    # get role
    # -------------------------
    role_result = await db.execute(
        select(Role).where(Role.code == UserRole.SUPERADMIN.value)
    )
    role = role_result.scalar_one_or_none()

    if not role:
        print("❌ Run bootstrap first")
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
    )

    db.add(user)

    print("✅ SuperAdmin created")
