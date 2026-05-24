from sqlalchemy import delete, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

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
    existing_permissions = {p.slug: p for p in result.scalars().all()}

    for slug in Permissions.all():
        if slug not in existing_permissions:
            # Create a human-readable name from the slug
            name = slug.replace(".", " ").replace("_", " ").title()
            db.add(Permission(slug=slug, name=name))
            print(f"  + Permission: {slug}")

    await db.flush()

    result = await db.execute(select(Permission))
    permissions_map = {p.slug: p for p in result.scalars().all()}
    print(f"✅ {len(permissions_map)} permissions ready")

    # =========================
    # 2. ROLES
    # =========================
    print("👥 Setting up roles...")
    result = await db.execute(select(Role))
    existing_roles = {r.slug: r for r in result.scalars().all()}

    role_descriptions = {
        "superadmin": "Super Administrator - Complete system access",
        "admin": "Administrator - Full operational control, manages users, regions, services",
        "operator": "Operator - Enters data, creates assets, requests repairs",
        "approver": "Approver - Approves/rejects requests (assignments, transfers, repairs)",
        "analyst": "Analyst - Read-only analytics, dashboards, exports (no modifications)",
    }

    for role_enum in UserRole:
        role_slug = str(role_enum.value)

        if role_slug not in existing_roles:
            role = Role(
                slug=role_slug,
                name=role_slug.replace("_", " ").title(),
                description=role_descriptions.get(role_slug, ""),
            )
            db.add(role)
            existing_roles[role_slug] = role
            print(f"  + Role: {role_slug}")

    await db.flush()
    print(f"✅ {len(existing_roles)} roles ready")

    # =========================
    # 3. ROLE-PERMISSION MAPPING
    # =========================
    print("⛓️  Mapping permissions to roles...")

    for role_slug, perm_slugs in ROLE_PERMISSIONS.items():
        role = existing_roles.get(role_slug)

        if not role:
            print(f"  ⚠️  Role '{role_slug}' not found in ROLE_PERMISSIONS")
            continue

        # Clear old mappings
        await db.execute(
            delete(role_permissions).where(role_permissions.c.role_id == role.id)
        )

        # Insert new mappings
        rows = []
        for p_slug in perm_slugs:
            perm = permissions_map.get(p_slug)
            if perm:
                rows.append(
                    {
                        "role_id": role.id,
                        "permission_id": perm.id,
                    }
                )
            else:
                print(f"  ⚠️  Permission '{p_slug}' not found for role '{role_slug}'")

        if rows:
            seen = set()
            unique_rows = []
            for row in rows:
                key = (row["role_id"], row["permission_id"])
                if key not in seen:
                    seen.add(key)
                    unique_rows.append(row)

            stmt = (
                pg_insert(role_permissions)
                .values(unique_rows)
                .on_conflict_do_nothing(index_elements=["role_id", "permission_id"])
            )
            await db.execute(stmt)
            print(f"  ✓ {role_slug}: {len(unique_rows)} permissions mapped")

    await db.flush()

    print("✅ RBAC Bootstrap Complete!")
    print(f"   - Permissions: {len(permissions_map)}")
    print(f"   - Roles: {len(existing_roles)}")
