from sqlalchemy import delete, insert, select

from core.security.rbac.permissions import ROLE_PERMISSIONS, Permissions
from db.models.enums import UserRole

# 👉 импортируй свою association table
from db.models.users.permission import (
    Permission,
    Role,
    role_permissions,  # 👈 ВАЖНО
)


async def seed_rbac(db):
    print("🔐 Seeding RBAC...")

    # =========================
    # 1. PERMISSIONS
    # =========================
    result = await db.execute(select(Permission))
    existing_permissions = {p.code: p for p in result.scalars().all()}

    for code in Permissions.all():
        if code not in existing_permissions:
            db.add(Permission(code=code, name=code.replace(".", " ").title()))
            print(f"  + New permission: {code}")

    await db.flush()

    result = await db.execute(select(Permission))
    permissions_map = {p.code: p for p in result.scalars().all()}

    # =========================
    # 2. ROLES
    # =========================
    result = await db.execute(select(Role))
    existing_roles = {r.code: r for r in result.scalars().all()}

    for role_enum in UserRole:
        role_code = str(role_enum.value)

        if role_code not in existing_roles:
            role = Role(code=role_code, name=role_code.upper())
            db.add(role)
            existing_roles[role_code] = role
            print(f"  + New role: {role_code}")

    await db.flush()

    # =========================
    # 3. MAPPING (🔥 БЕЗ ORM RELATIONSHIP)
    # =========================
    print("⛓️  Mapping permissions to roles...")

    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = existing_roles.get(role_code)

        if not role:
            continue

        # ❗ Удаляем старые связи напрямую
        await db.execute(
            delete(role_permissions).where(role_permissions.c.role_id == role.id)
        )

        # ❗ Вставляем новые
        rows = []
        for p_code in perm_codes:
            perm = permissions_map.get(p_code)
            if perm:
                rows.append(
                    {
                        "role_id": role.id,
                        "permission_id": perm.id,
                    }
                )

        if rows:
            await db.execute(insert(role_permissions), rows)

    await db.flush()

    print("✅ RBAC bootstrap completed successfully")
