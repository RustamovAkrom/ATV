from fastapi import Depends
from repositories.user_repo import UserRepository, get_user_repo
from repositories.auth_repo import AuthRepository, get_auth_repo
from repositories.password_reset_repo import PasswordResetRepository, get_reset_repo
from services.auth_service import AuthService
from services.security_service import SecurityService


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    auth_repo: AuthRepository = Depends(get_auth_repo),
) -> AuthService:
    return AuthService(user_repo, auth_repo)


def get_security_service(
    user_repo: UserRepository = Depends(get_user_repo),
    auth_repo: AuthRepository = Depends(get_auth_repo),
    reset_repo: PasswordResetRepository = Depends(get_reset_repo)
) -> SecurityService:
    return SecurityService(user_repo, auth_repo, reset_repo)
