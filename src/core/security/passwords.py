# core/security/passwords.py

import hashlib
from typing import Optional

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from core.config import get_settings
from core.logger import configure_logger

logger = configure_logger()
settings = get_settings()


# =========================
# CONFIG
# =========================
BCRYPT_ROUNDS = getattr(settings, "BCRYPT_ROUNDS", 12)


# =========================
# HASH ENGINE
# =========================
password_hash = PasswordHash(
    (
        BcryptHasher(
            rounds=BCRYPT_ROUNDS,
        ),
    )
)


# =========================
# INTERNAL
# =========================
def _normalize(password: str) -> str:
    """
    Fix bcrypt 72-byte limit
    + normalize input for consistency
    """
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# PUBLIC API
# =========================
def hash_password(password: str) -> str:
    return password_hash.hash(_normalize(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(
            _normalize(plain_password),
            hashed_password,
        )
    except Exception as exc:
        print("Password verify failed")
        logger.warning("password_verify_failed", error=str(exc))
        return False
