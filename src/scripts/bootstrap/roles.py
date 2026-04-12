
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sqlalchemy import select

from db.models.users.permission import Role, Permission, role_permissions
from db.models.enums import UserRole


DEFAULT_PERMISSIONS = [
    "users.read",
    "users.write",
    "users.delete",
    "users.manage",
    "assets.read",
    "assets.write",
]

ROLE_MATRIX = {
    UserRole.SUPERADMIN: DEFAULT_PERMISSIONS,
    UserRole.ADMIN: DEFAULT_PERMISSIONS,
    UserRole.MODERATOR: [
        "users.read",
        "assets.read",
    ],
    UserRole.ANALYTIC: [
        "assets.read",
    ],
}

async def seed_roles_permissions(db):
    # --- permissions ---
    result = await db.execute(select(Permission))
    existing_perms = {p.code: p for p in result.scalars()}

    for code in DEFAULT_PERMISSIONS:
        if code not in existing_perms:
            perm = Permission(code=code, name=code)
            db.add(perm)
            await db.flush()
            existing_perms[code] = perm

    # --- roles ---
    result = await db.execute(select(Role))
    roles = {r.code: r for r in result.scalars()}

    for role_enum, perms in ROLE_MATRIX.items():
        role_code = role_enum.value

        if role_code not in roles:
            role = Role(code=role_code, name=role_code.upper())
            db.add(role)
            await db.flush()
            roles[role_code] = role

        role = roles[role_code]

        # 🔥 ВАЖНО: добавляем только новые связи
        for perm_code in perms:
            perm = existing_perms[perm_code]

            stmt = pg_insert(role_permissions).values(
                role_id=role.id,
                permission_id=perm.id,
            ).on_conflict_do_nothing()

            await db.execute(stmt)
