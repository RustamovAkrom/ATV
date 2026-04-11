from fastapi import Depends
from repositories.user_repo import UserRepository, get_user_repo
from repositories.auth_repo import AuthRepository, get_auth_repo
from services.auth_service import AuthService


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    auth_repo: AuthRepository = Depends(get_auth_repo),
) -> AuthService:
    return AuthService(user_repo, auth_repo)
