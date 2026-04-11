from sqlalchemy import select, insert, delete
from db.models.users.role import Role
from db.models.users.permission import Permission
from db.models.users.associations import role_permissions


ROLES = {
    "admin": [
        "users.read",
        "users.write",
        "users.delete",
        "users.manage",
    ],
    "user": ["users.read"],
}


async def seed_roles(db):
    result = await db.execute(select(Role))
    roles = {r.role: r for r in result.scalars().all()}

    # permissions
    perm_result = await db.execute(select(Permission))
    permissions = {p.code: p for p in perm_result.scalars().all()}

    for role_name, perms in ROLES.items():
        if role_name not in roles:
            role = Role(name=role_name)
            db.add(role)
            await db.flush()
            roles[role_name] = role

        role = roles[role_name]


        # delete old relationships
        await db.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == role.id
            )
        )

        # create new
        await db.execute(
            insert(role_permissions),
            [
                {
                    "role_id": role.id,
                    "permission_id": permissions[p].id
                }
                for p in perms
            ]
        )
