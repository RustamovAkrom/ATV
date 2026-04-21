from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.security.rbac.permissions import ROLE_PERMISSIONS, Permissions
from db.models.enums import UserRole
from db.models.users.permission import Permission, Role


async def seed_rbac(db):
    print("🔐 Seeding RBAC...")

    # =========================
    # 1. СИНХРОНИЗАЦИЯ PERMISSIONS
    # =========================
    # Получаем все существующие права из базы
    result = await db.execute(select(Permission))
    existing_permissions = {p.code: p for p in result.scalars().all()}

    all_defined_perms = Permissions.all()

    for code in all_defined_perms:
        if code not in existing_permissions:
            new_perm = Permission(code=code, name=code.replace(".", " ").title())
            db.add(new_perm)
            print(f"  + New permission: {code}")

    # Сначала фиксируем новые пермишены, чтобы они получили ID
    await db.flush()

    # Перезагружаем словарь пермишенов после вставки
    result = await db.execute(select(Permission))
    permissions_map = {p.code: p for p in result.scalars().all()}

    # =========================
    # 2. СИНХРОНИЗАЦИЯ ROLES
    # =========================
    # Загружаем роли вместе с их текущими правами (selectinload предотвращает LazyLoad error)
    result = await db.execute(select(Role).options(selectinload(Role.permissions)))
    existing_roles = {r.code: r for r in result.scalars().all()}

    for role_enum in UserRole:
        role_code = str(role_enum.value)
        if role_code not in existing_roles:
            new_role = Role(
                code=role_code,
                name=role_code.upper(),
            )
            db.add(new_role)
            existing_roles[role_code] = new_role
            print(f"  + New role: {role_code}")

    await db.flush()

    # =========================
    # 3. ПРИВЯЗКА ПРАВ К РОЛЯМ (ROLE_PERMISSIONS)
    # =========================
    print("⛓️  Mapping permissions to roles...")

    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = existing_roles.get(role_code)

        if not role:
            print(f"  ⚠️  Role {role_code} not found in DB, skipping...")
            continue

        # Формируем список объектов Permission для данной роли
        target_permissions = []
        for p_code in perm_codes:
            perm_obj = permissions_map.get(p_code)
            if perm_obj:
                target_permissions.append(perm_obj)
            else:
                print(f"  ⚠️  Permission {p_code} defined in ROLE_PERMISSIONS but not in Permissions class!")

        # Обновляем связи. SQLAlchemy сама удалит старые и добавит новые в таблице ассоциаций
        role.permissions = target_permissions

    try:
        await db.flush()
        print("✅ RBAC bootstrap completed successfully")
    except Exception as e:
        print(f"❌ Error during RBAC seeding: {e}")
        raise e
