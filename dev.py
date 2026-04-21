import hashlib
from typing import Optional

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

password_hash = PasswordHash((BcryptHasher(rounds=12), ))


def _normalize(password: str) -> str:
    """
    Fix bcrypt 72-byte limit
    + normalize input for consistency
    """
    return hashlib.sha256(password.encode()).hexdigest()


def hash_password(password: str) -> str:
    return password_hash.hash(_normalize(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(_normalize(plain_password), hashed_password)

password = "Akromjon2007"

hashed = hash_password(password)

print(verify_password(password, hashed))

hashed_password = "$2b$12$omwxwrHnXI8wfM1Y4OlFBODB2OsJHOb9X.Q.ak6zL06jU4PtrfiXC"

print(verify_password("Akromjon2007", hashed_password))
