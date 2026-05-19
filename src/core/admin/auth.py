from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from loguru import logger
from core.security.passwords import verify_password
from db.models.users.user import User
from db.models.enums import UserRole
from core.database.db_sync import get_sync_session_factory
from core.config import get_settings

settings = get_settings()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            logger.warning(f"Admin login failed: missing credentials from {request.client.host}")
            return False

        session_factory = get_sync_session_factory()
        with session_factory() as session:
            user = session.query(User).filter(User.login == username).first()

            if not user:
                logger.warning(f"Admin login failed: user '{username}' not found from {request.client.host}")
                return False

            # Проверка пароля и прав супер-админа
            is_password_valid = verify_password(password, user.password_hash)
            is_superadmin = user.role and user.role.slug == UserRole.SUPERADMIN.value
            is_active = user.status and user.status.value == "active"

            if is_password_valid and is_superadmin and is_active:
                request.session["user_id"] = str(user.id)
                request.session["user"] = user.login
                request.session["role"] = user.role.slug
                logger.info(f"Admin login successful: '{username}' from {request.client.host}")
                return True

            reason = []
            if not is_password_valid:
                reason.append("invalid password")
            if not is_superadmin:
                reason.append("not superadmin")
            if not is_active:
                reason.append("user inactive")

            logger.warning(f"Admin login failed for '{username}': {', '.join(reason)} from {request.client.host}")
            return False

    async def logout(self, request: Request) -> bool:
        user = request.session.get("user", "unknown")
        request.session.pop("user_id", None)
        request.session.pop("user", None)
        request.session.pop("role", None)
        logger.info(f"Admin logout: '{user}' from {request.client.host}")
        return True

    async def authenticate(self, request: Request) -> bool:
        is_authenticated = "user" in request.session

        # Проверка, что пользователь ещё существует в БД и активен
        if is_authenticated and "user_id" in request.session:
            session_factory = get_sync_session_factory()
            with session_factory() as session:
                user = session.query(User).filter(User.id == request.session["user_id"]).first()
                if not user or user.status.value != "active":
                    await self.logout(request)
                    return False

        return is_authenticated
