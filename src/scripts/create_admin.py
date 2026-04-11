from sqlalchemy import select
from db.models.users.user import User
from db.models.users.role import Role
from core.security.passwords import hash_password


async def create_admin(db):
    login = input("Login: ")
    email = input("Email: ")
    password = input("Password: ")

    result = await db.execute(select(User).where(User.login == login))
    if result.scalar_one_or_none():
        print("User already exists")
        return

    role_result = await db.execute(
        select(Role).where(Role.name == "admin")
    )
    role = role_result.scalar_one_or_none()

    if not role:
        print("Admin role not found. Run seed_roles first.")
        return

    db.add(
        User(
            login=login,
            password_hash=hash_password(password),
            email=email,
            role_id=role.id,
        )
    )
    db.commit()

    print("Admin created")
