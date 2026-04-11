# scripts/seed.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, insert, delete
from db.models.users.associations import role_permissions
from db.models.users.role import Role
from db.models.users.permission import Permission
from db.models.users.user import User
from core.security.passwords import hash_password


# ------------------------
# CONFIG
# ------------------------

PERMISSIONS = [
    "users.read",
    "users.write",
    "users.delete",
    "roles.manage",
]

ROLES = {
    "admin": PERMISSIONS,
    "user": ["users.read"],
}

ADMIN = {
    "login": "admin",
    "password": "admin123",  # ❗ заменить через env в production
}


# ------------------------
# PERMISSIONS
# ------------------------
async def seed_permissions(db: AsyncSession):
    result = await db.execute(select(Permission.code))
    existing_codes = set(result.scalars().all())

    new_permissions = [
        Permission(code=code)
        for code in PERMISSIONS
        if code not in existing_codes
    ]

    if new_permissions:
        db.add_all(new_permissions)


# ------------------------
# ROLES
# ------------------------
async def seed_roles(db: AsyncSession):
    # роли
    result = await db.execute(select(Role))
    roles = {r.name: r for r in result.scalars().all()}

    # permissions
    perm_result = await db.execute(select(Permission))
    permissions = {p.code: p for p in perm_result.scalars().all()}

    for role_name, perms in ROLES.items():
        # создать роль если нет
        if role_name not in roles:
            role = Role(name=role_name)
            db.add(role)
            await db.flush()
            roles[role_name] = role

        role = roles[role_name]

        # 🔥 УДАЛИТЬ старые связи
        await db.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == role.id
            )
        )

        # 🔥 СОЗДАТЬ новые связи (bulk insert)
        await db.execute(
            insert(role_permissions),
            [
                {
                    "role_id": role.id,
                    "permission_id": permissions[p].id,
                }
                for p in perms
            ],
        )

# ------------------------
# ADMIN USER
# ------------------------
async def seed_admin(db: AsyncSession):
    result = await db.execute(
        select(User).where(User.login == ADMIN["login"])
    )
    user = result.scalar_one_or_none()

    if user:
        return

    role_result = await db.execute(
        select(Role).where(Role.name == "admin")
    )
    admin_role = role_result.scalar_one()

    db.add(
        User(
            login=ADMIN["login"],
            password_hash=hash_password(ADMIN["password"]),
            role_id=admin_role.id,
        )
    )


# ------------------------
# MAIN
# ------------------------
async def seed_all(db: AsyncSession):
    # 🔥 порядок важен
    await seed_permissions(db)
    await db.flush()

    await seed_roles(db)
    await db.flush()

    await seed_admin(db)
