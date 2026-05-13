import re

from sqlalchemy.exc import IntegrityError

from core.exceptions.errors import BadRequest
from utils.slug import slugify


def validate_name(name: str) -> str:
    if not name or not name.strip():
        raise BadRequest("Name cannot be empty")

    name = name.strip()
    if len(name) < 2:
        raise BadRequest("Name too short")

    if len(name) > 100:
        raise BadRequest("Name is too long")

    if not re.search(r"[a-zA-Z0-9]", name):
        raise BadRequest("Invalid name")

    return name


def normalize_name(name: str) -> str:
    return name.strip().lower()


async def ensure_unique_name(repo, normalized: str):
    existing = await repo.get_by_normalized_name(normalized)
    if existing:
        raise BadRequest("Already exists")


async def ensure_unique_code(repo, code: str):
    existing = await repo.get_by_code(code)
    if existing:
        raise BadRequest("Similar entity already exists")


async def safe_create(repo, obj):
    try:
        return await repo.create(obj)
    except IntegrityError as e:
        raise BadRequest("Already exists") from e
    except Exception as e:
        raise BadRequest("Failed to create") from e


async def validate_and_prepare(repo, name: str):
    # 1. validate
    name = validate_name(name)
    normalized = normalize_name(name)

    # 2. check name
    await ensure_unique_name(repo, normalized)

    # 3. generate slug
    code = slugify(name)

    if not code:
        raise BadRequest("Invalid name")

    # 4. check code
    await ensure_unique_code(repo, code)

    return name, code
