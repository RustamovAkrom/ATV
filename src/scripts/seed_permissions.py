from sqlalchemy import select
from db.models.users.permission import Permission

PERMISSIONS = [
    "users.read",
    "users.write",
    "users.delete",
    "users.manage",
]

async def seed_permissions(db):
    result = await db.execute(select(Permission.code))
    existing = set(result.scalars().all())

    new = [
        Permission(code=code)
        for code in PERMISSIONS
        if code not in existing
    ]

    if new:
        db.add_all(new)
