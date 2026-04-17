from datetime import timedelta

from core.config import get_settings
from core.exceptions.errors import InvalidToken
from core.security.passwords import hash_password
from db.models.auth.password_reset import PasswordReset
from repositories.auth_repo import AuthRepository
from repositories.password_reset_repo import PasswordResetRepository
from repositories.user_repo import UserRepository
from tasks.email_task import send_password_reset_email_task
from utils.reset_tokens import hash_token
import utils.reset_tokens as tokens
from utils.helpers import utc_now
from core.logger import configure_logger


class SecurityService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_repo: AuthRepository,
        reset_repo: PasswordResetRepository,
    ):
        self.settings = get_settings()
        self.logger = configure_logger()
        self.user_repo = user_repo
        self.auth_repo = auth_repo
        self.reset_repo = reset_repo

    async def request_password_reset(self, login: str) -> None:
        user = await self.user_repo.get_by_identity(login)

        if not user:
            return

        self.logger.info(f"Password reset requested user={user.id}")

        token = tokens.generate_token()
        token_hash = hash_token(token)

        await self.reset_repo.clean_old(user.id)

        await self.reset_repo.create(
            PasswordReset(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=utc_now() + timedelta(minutes=30),
            )
        )
        try:
            # Send change url to email user
            if self.settings.ENV == "prod":
                print("[PROD] password reset task")
                send_password_reset_email_task.delay(user.email, token)
            else:
                print("[DEV] Password reset task")
                self.logger.info(f"[DEV] Reset token for {user.email}: {token}")

        except Exception as e:
            print("Request password reset error: ", e)
            self.logger.exception("Password reset delivery failed")

    async def reset_password(self, token: str, new_password: str):
        token_hash = tokens.hash_token(token)

        reset = await self.reset_repo.use_token(token_hash)
        if not reset:
            raise InvalidToken()

        user = await self.user_repo.get_by_id(reset.user_id)
        if not user:
            raise InvalidToken()

        # update password
        user.password_hash = hash_password(new_password)
        user.last_password_change = utc_now()

        # revoke sessions
        await self.auth_repo.revoke_all_by_user(user.id)
        await self.reset_repo.clean_old(user.id)

        self.logger.info(f"Password reset success user={user.id}")
