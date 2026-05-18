from core.security.passwords import hash_password
from db.models.enums import UserRole, UserStatus
from db.models.users.permission import Role
from db.models.users.user import User


async def create_user(dbsession, login="user", password="password"):
    role = Role(name="User", slug=UserRole.ADMIN.value)
    dbsession.add(role)
    await dbsession.flush()

    user = User(
        login=login,
        password_hash=hash_password(password),
        email=f"{login}@test.com",
        phone=f"+99890000{hash(login) % 100000}",
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
    )
    dbsession.add(user)
    await dbsession.commit()

    return user
