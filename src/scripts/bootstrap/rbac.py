from sqlalchemy import select

from db.models.enums import UserRole
from db.models.users.permission import Permission, Role
from core.security.permissions import Permissions, ROLE_PERMISSIONS


async def seed_rbac(db):
    print("🔐 Seeding RBAC...")

    # =========================
    # 1. PERMISSIONS
    # =========================
    existing_permissions = {
        p.code: p
        for p in (await db.execute(select(Permission))).scalars()
    }

    # ✅ используем registry
    for code in Permissions.all():
        if code not in existing_permissions:
            db.add(Permission(code=code, name=code))

    await db.flush()

    # reload
    permissions = {
        p.code: p
        for p in (await db.execute(select(Permission))).scalars()
    }

    # =========================
    # 2. ROLES
    # =========================
    existing_roles = {
        r.code: r
        for r in (await db.execute(select(Role))).scalars()
    }

    # ✅ используем enum (единый источник)
    for role in UserRole:
        if role.value not in existing_roles:
            db.add(
                Role(
                    code=role.value,
                    name=role.value.upper(),
                )
            )

    await db.flush()

    # reload
    roles = {
        r.code: r
        for r in (await db.execute(select(Role))).scalars()
    }

    # =========================
    # 3. ASSIGN PERMISSIONS
    # =========================
    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = roles.get(role_code)

        if not role:
            continue  # safeguard

        role.permissions = [
            permissions[p]
            for p in perm_codes
            if p in permissions  # safeguard
        ]

    await db.flush()

    print("✅ RBAC ready")
