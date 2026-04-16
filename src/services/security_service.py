from datetime import datetime, timedelta, timezone

from core.config import get_settings
from core.exceptions.errors import InvalidToken
from core.security.passwords import hash_password
from db.models.auth.password_reset import PasswordReset
from repositories.auth_repo import AuthRepository
from repositories.password_reset_repo import PasswordResetRepository
from repositories.user_repo import UserRepository
from tasks.email_task import send_password_reset_email_task
from utils.reset_tokens import generate_token, hash_token

def utc_now():
    return datetime.now(timezone.utc)


class SecurityService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_repo: AuthRepository,
        reset_repo: PasswordResetRepository,
    ):
        self.settings = get_settings()
        self.user_repo = user_repo
        self.auth_repo = auth_repo
        self.reset_repo = reset_repo

    async def request_password_reset(self, login: str) -> None:
        user = await self.user_repo.get_by_login(login)

        if not user:
            return

        token = generate_token()
        token_hash = hash_token(token)

        await self.reset_repo.create(
            PasswordReset(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=utc_now() + timedelta(minutes=30),
            )
        )

        # Send change url to email user
        send_password_reset_email_task.delay(user.email, token)


    async def reset_password(self, token: str, new_password: str):
        token_hash = hash_token(token)

        reset = await self.reset_repo.get_valid(token_hash)

        if not reset:
            raise InvalidToken()

        user = await self.user_repo.get_by_id(reset.user_id)

        if not user:
            raise InvalidToken()

        # update password
        user.password_hash = hash_password(new_password)
        user.last_password_change = datetime.utcnow()

        # revoke sessions
        await self.auth_repo.revoke_all_by_user(user.id)

        # mark token used
        await self.reset_repo.mark_used(reset.id)
