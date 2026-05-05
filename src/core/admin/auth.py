from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from core.security.passwords import verify_password
from db.models.users.user import User
from db.models.enums import UserRole
from core.database.db_sync import get_sync_session_factory


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        # Check against DB
        session_factory = get_sync_session_factory()
        with session_factory() as session:
            user = session.query(User).filter(User.login == username).first()
            if user and verify_password(password, user.password_hash) and user.role.code == UserRole.SUPERADMIN.value:
                request.session["user_id"] = str(user.id)
                request.session["user"] = user.login
                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.pop("user_id", None)
        request.session.pop("user", None)
        return True

    async def authenticate(self, request: Request) -> bool:
        return "user" in request.session
