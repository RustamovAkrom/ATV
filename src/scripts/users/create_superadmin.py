# src/scripts/users/create_superadmin.py

from sqlalchemy import select
from db.models.users.user import User
from db.models.users.permission import Role
from db.models.enums import UserRole
from core.security.passwords import hash_password


async def create_superadmin(db):
    print("=== Create SuperAdmin ===")

    login = input("Login: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip() or None
    phone = input("Phone Example(+998991234567): ").strip() or None

    # check existing
    result = await db.execute(select(User).where(User.login == login))
    if result.scalar_one_or_none():
        print("❌ User already exists")
        return

    # get role
    role_result = await db.execute(
        select(Role).where(Role.code == UserRole.SUPERADMIN.value)
    )
    role = role_result.scalar_one_or_none()

    if not role:
        print("❌ Roles not initialized. Run bootstrap first.")
        return

    user = User(
        login=login,
        password_hash=hash_password(password),
        email=email,
        phone=phone,
        role_id=role.id,
    )

    db.add(user)

    print("✅ SuperAdmin created")
