from pwdlib import PasswordHash

from core.logger import configure_logger
from core.config import get_settings

logger = configure_logger()
settings = get_settings()
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash user password using bcrypt.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    """
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception as exc:
        logger.warning("Password verification failed", error=str(exc))
        return False
