from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.exceptions.errors import AuthenticationError, BadRequest, NotFound
from schemas.users.user import AdminUserUpdateSchema, UserCreateSchema, UserUpdateSchema
from services.users.user_service import UserService

pytestmark = pytest.mark.anyio


class _Repo:
    def __init__(self):
        self.users = {}

    async def list(self, pagination):
        return list(self.users.values())

    async def search(self, query, pagination):
        return [u for u in self.users.values() if query in u.login]

    async def get_by_id(self, user_id, include_inactive=False):
        return self.users.get(user_id)

    async def exists_by_email(self, email):
        return any(u.email == email for u in self.users.values())

    async def exists_by_login(self, login):
        return any(u.login == login for u in self.users.values())

    async def create(self, user):
        user.id = uuid4()
        user.password_hash = user.password_hash
        self.users[user.id] = user
        return user

    async def update(self, user_id, data):
        u = self.users.get(user_id)
        if u:
            for k, v in data.items():
                setattr(u, k, v)

    async def set_password(self, user_id, password_hash):
        self.users[user_id].password_hash = password_hash

    async def change_status(self, user_id, status):
        if user_id in self.users:
            self.users[user_id].status = status


class _RBAC:
    async def get_role(self, role_id):
        return SimpleNamespace(id=role_id)


@pytest.fixture
def user_service(monkeypatch):
    import services.users.user_service as module

    repo = _Repo()
    rbac = _RBAC()
    service = UserService(repo, rbac)

    monkeypatch.setattr(module, "verify_password", lambda raw, hashed: raw == "oldpass")
    monkeypatch.setattr(module, "hash_password", lambda p: f"hash:{p}")
    return service, repo


class TestUserService:
    async def test_create_get_update_and_admin_update(self, user_service):
        service, repo = user_service
        role_id = uuid4()
        created = await service.create(
            UserCreateSchema(
                login="user1",
                email="user1@example.com",
                phone="+998901234567",
                password="secret1",
                role_id=role_id,
            )
        )
        got = await service.get(created.id)
        assert got.login == "user1"

        updated = await service.update(created.id, UserUpdateSchema(first_name="A"))
        assert updated.first_name == "A"

        admin_updated = await service.admin_update(
            created.id,
            AdminUserUpdateSchema(role_id=role_id, status="active", position="Manager"),
        )
        assert admin_updated.position == "Manager"

    async def test_create_duplicate_email_and_login(self, user_service):
        service, _ = user_service
        role_id = uuid4()
        await service.create(
            UserCreateSchema(
                login="usr1",
                email="u1@example.com",
                phone="+998901234567",
                password="secret1",
                role_id=role_id,
            )
        )
        with pytest.raises(BadRequest):
            await service.create(
                UserCreateSchema(
                    login="usr2",
                    email="u1@example.com",
                    phone="+998901111111",
                    password="secret1",
                    role_id=role_id,
                )
            )

    async def test_get_not_found_and_change_password_errors(self, user_service):
        service, repo = user_service
        with pytest.raises(BadRequest):
            await service.get(uuid4())

        role_id = uuid4()
        user = await service.create(
            UserCreateSchema(
                login="pwd1",
                email="pwd1@example.com",
                phone="+998901234568",
                password="secret1",
                role_id=role_id,
            )
        )

        with pytest.raises(AuthenticationError):
            await service.change_password(user.id, "wrong", "newpass")

        await service.change_password(user.id, "oldpass", "newpass")
        assert repo.users[user.id].password_hash == "hash:newpass"

    async def test_activate_archive_block(self, user_service):
        service, repo = user_service
        role_id = uuid4()
        user = await service.create(
            UserCreateSchema(
                login="stat1",
                email="stat1@example.com",
                phone="+998901234569",
                password="secret1",
                role_id=role_id,
            )
        )

        await service.activate(user.id)
        assert repo.users[user.id].status == "active"
        await service.archive(user.id)
        assert repo.users[user.id].status == "archived"
        await service.block(user.id)
        assert repo.users[user.id].status == "blocked"

    async def test_update_not_found(self, user_service):
        service, _ = user_service
        with pytest.raises(NotFound):
            await service.update(uuid4(), UserUpdateSchema(first_name="x"))
