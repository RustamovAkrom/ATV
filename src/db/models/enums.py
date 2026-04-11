from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    ARCHIVED = "archived"
