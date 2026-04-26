from sqlalchemy import delete, insert, select

from core.security.rbac.permissions import ROLE_PERMISSIONS, Permissions
from db.models.enums import UserRole

# Import association tables and models
from db.models.users.permission import (
    Permission,
    Role,
    role_permissions,
    user_permissions,
)


async def seed_rbac(db):
    """
    Bootstrap RBAC system with default permissions and roles.
    This function is idempotent and safe to run multiple times.

    Process:
    1. Create all permissions from registry if they don't exist
    2. Create all default roles if they don't exist
    3. Map permissions to roles based on ROLE_PERMISSIONS configuration
    """
    print("🔐 Seeding RBAC System...")

    # =========================
    # 1. PERMISSIONS
    # =========================
    print("📋 Setting up permissions...")
    result = await db.execute(select(Permission))
    existing_permissions = {p.code: p for p in result.scalars().all()}

    for code in Permissions.all():
        if code not in existing_permissions:
            # Create a human-readable name from the code
            name = code.replace(".", " ").replace("_", " ").title()
            db.add(Permission(code=code, name=name))
            print(f"  + Permission: {code}")

    await db.flush()

    result = await db.execute(select(Permission))
    permissions_map = {p.code: p for p in result.scalars().all()}
    print(f"✅ {len(permissions_map)} permissions ready")

    # =========================
    # 2. ROLES
    # =========================
    print("👥 Setting up roles...")
    result = await db.execute(select(Role))
    existing_roles = {r.code: r for r in result.scalars().all()}

    role_descriptions = {
        "superadmin": "Super Administrator - Complete system access",
        "admin": "Administrator - Full operational control",
        "moderator": "Moderator - Regional/operational management",
        "analytic": "Analyst - Read-only analytics and audit access",
        "region_admin": "Region Administrator - Region-scoped admin",
        "service_manager": "Service Manager - Service-scoped management",
        "operator": "Operator - Basic operational access",
        "approver": "Approver - Approval workflow focus",
        "auditor": "Auditor - Audit and compliance focus",
    }

    for role_enum in UserRole:
        role_code = str(role_enum.value)

        if role_code not in existing_roles:
            role = Role(
                code=role_code,
                name=role_code.replace("_", " ").title(),
                description=role_descriptions.get(role_code, ""),
            )
            db.add(role)
            existing_roles[role_code] = role
            print(f"  + Role: {role_code}")

    await db.flush()
    print(f"✅ {len(existing_roles)} roles ready")

    # =========================
    # 3. ROLE-PERMISSION MAPPING
    # =========================
    print("⛓️  Mapping permissions to roles...")

    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = existing_roles.get(role_code)

        if not role:
            print(f"  ⚠️  Role '{role_code}' not found in ROLE_PERMISSIONS")
            continue

        # Clear old mappings
        await db.execute(
            delete(role_permissions).where(role_permissions.c.role_id == role.id)
        )

        # Insert new mappings
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
            else:
                print(f"  ⚠️  Permission '{p_code}' not found for role '{role_code}'")

        if rows:
            await db.execute(insert(role_permissions), rows)
            print(f"  ✓ {role_code}: {len(rows)} permissions mapped")

    await db.flush()

    print("✅ RBAC Bootstrap Complete!")
    print(f"   - Permissions: {len(permissions_map)}")
    print(f"   - Roles: {len(existing_roles)}")

