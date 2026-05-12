import uuid
import os
import aiofiles
import csv
from io import StringIO
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from api.dependencies.users import get_user_service
from api.dependencies.paginations import get_pagination
from core.cache.decorators import cached, invalidate_cache
from core.exceptions.errors import BadRequest
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import UserPermissions
from db.models.users.user import User
from schemas.auth import CurrentUserSchema
from schemas.pagination import PaginationParamsSchema

from schemas.users import (
    AdminUserUpdateSchema,
    ChangePasswordRequestSchema,
    UserCreateSchema,
    UserOutSchema,
    UserUpdateSchema,
    UserAvatarUpdateSchema,
)
from services.users.user_service import UserService
from schemas.common import StatusResponse
from core.config import get_settings


router = APIRouter(prefix="/users", tags=["Users"])


def _to_user_out(user: User) -> UserOutSchema:
    role = getattr(user.role, "code", None)
    permissions = [
        str(getattr(permission, "code", getattr(permission, "value", permission)))
        for permission in (getattr(user, "permissions", None) or [])
    ]

    return UserOutSchema(
        id=user.id,
        login=user.login,
        email=user.email,
        phone=user.phone,
        role=str(role).lower() if role else None,
        permissions=permissions,
        first_name=getattr(user, "first_name", None),
        last_name=getattr(user, "last_name", None),
        status=getattr(user, "status", None),
        created_at=getattr(user, "created_at", None),
        updated_at=getattr(user, "updated_at", None),
        position=getattr(user, "position", None),
        department=getattr(user, "department", None),
        employment_type=getattr(user, "employment_type", None),
        date_of_birth=getattr(user, "date_of_birth", None),
        gender=getattr(user, "gender", None),
        badge_number=getattr(user, "badge_number", None),
        passport_number=getattr(user, "passport_number", None),
        avatar_url=getattr(user, "avatar_url", None),
        hired_at=getattr(user, "hired_at", None),
        dismissed_at=getattr(user, "dismissed_at", None),
        language=getattr(user, "language", None),
        timezone=getattr(user, "timezone", None),
        last_login=getattr(user, "last_login", None),
        assigned_region_id=getattr(user, "assigned_region_id", None),
        assigned_service_id=getattr(user, "assigned_service_id", None),
    )

### ME -----------------------------------------
@router.get("/me", response_model=UserOutSchema)
@cached(ttl=60, tags=("users:me",))
async def me(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get(current_user.id)
    return _to_user_out(user)


@router.patch("/me", response_model=UserOutSchema)
@invalidate_cache(tags=("users:list", "users:search", "users:detail", "users:me"))
async def update_me(
    data: UserUpdateSchema,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.update(current_user.id, data)
    return _to_user_out(user)


@router.post("/me/change-password")
@invalidate_cache(tags=("users:me",))
async def change_password(
    data: ChangePasswordRequestSchema,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.change_password(
        current_user.id,
        data.old_password,
        data.new_password,
    )
    return StatusResponse(status="ok", message="Password changed successfully")


@router.post("/me/avatar", response_model=UserOutSchema)
@invalidate_cache(tags=("users:list", "users:search", "users:detail", "users:me"))
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    settings = get_settings()

    # Проверяем размер файла
    max_size = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.UPLOAD_MAX_SIZE_MB}MB"
        )

    # ВОТ ТУТ ОШИБКА - используем MIMETYPES для content_type, а не EXTENSIONS
    if file.content_type not in settings.UPLOAD_ALLOWED_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(settings.UPLOAD_ALLOWED_MIMETYPES)}"
        )

    avatar_dir = settings.BASE_DIR / settings.UPLOAD_AVATAR_DIR
    avatar_dir.mkdir(parents=True, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1].lower()

    # Проверяем расширение файла
    if file_extension not in settings.UPLOAD_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension not allowed. Allowed: {', '.join(settings.UPLOAD_ALLOWED_EXTENSIONS)}"
        )

    unique_filename = f"{uuid.uuid4()}{file_extension}"

    if len(unique_filename) > settings.UPLOAD_MAX_FILENAME_LENGTH:
        unique_filename = unique_filename[:settings.UPLOAD_MAX_FILENAME_LENGTH]

    file_path = avatar_dir / unique_filename

    try:
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    avatar_url = f"{settings.UPLOAD_AVATAR_URL_PREFIX}/{unique_filename}"

    user = await service.get(current_user.id)
    old_avatar_url = user.avatar_url

    user = await service.update_avatar(current_user.id, UserAvatarUpdateSchema(avatar_url=avatar_url))

    if old_avatar_url:
        old_avatar_path = settings.BASE_DIR / old_avatar_url.lstrip('/')
        if old_avatar_path.exists() and old_avatar_path.is_file():
            try:
                old_avatar_path.unlink()
            except Exception:
                pass

    return _to_user_out(user)


@router.delete("/me/avatar", response_model=UserOutSchema)
@invalidate_cache(tags=("users:list", "users:search", "users:detail", "users:me"))
async def delete_avatar(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    settings = get_settings()

    user = await service.get(current_user.id)

    if user.avatar_url:
        old_avatar_path = settings.BASE_DIR / user.avatar_url.lstrip('/')
        if old_avatar_path.exists() and old_avatar_path.is_file():
            try:
                old_avatar_path.unlink()
            except Exception as e:
                print(f"Failed to delete avatar file: {e}")

    user = await service.update_avatar(current_user.id, UserAvatarUpdateSchema(avatar_url=None))

    return _to_user_out(user)


@router.get("/me/avatar", response_class=FileResponse)
async def get_avatar(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get(current_user.id)

    if not user.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar not found")

    avatar_path = get_settings().BASE_DIR / user.avatar_url.lstrip("/")

    if not avatar_path.exists():
        raise HTTPException(status_code=404, detail="Avatar file not found")

    return FileResponse(
        path=avatar_path,
        media_type="image/jpeg",
        filename=avatar_path.name
    )


# USERS -----------------------------------------------------------------------------------------
@router.get("/export", dependencies=[Depends(UserPermissions.CanViewUsers)])
async def export_users(
    service: UserService = Depends(get_user_service),
    pagination: PaginationParamsSchema = Depends(get_pagination)
):
    users = await service.get_all(pagination)

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Login", "Email", "Phone", "First Name", "Last Name",
        "Position", "Department", "Employment Type", "Status", "Role",
        "Hired At", "Dismissed At", "Avatar URL"
    ])

    for user in users:
        writer.writerow([
            str(user.id), user.login, user.email, user.phone,
            user.first_name or "", user.last_name or "", user.position or "",
            user.department or "", user.employment_type or "", user.status or "",
            user.role or "", user.hired_at or "", user.dismissed_at or "", user.avatar_url or "",
        ])

    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
    )
    response.headers["Content-Disposition"] = "attachment; filename=user.csv"
    return response


@router.get(
    "/", response_model=list[UserOutSchema], dependencies=[Depends(UserPermissions.CanViewUsers)]
)
@cached(ttl=60, tags=("users:list",))
async def list_users(
    service: UserService = Depends(get_user_service),
    pagination: PaginationParamsSchema = Depends(),
):
    users = await service.get_all(pagination)
    return [_to_user_out(user) for user in users]


@router.post("/", response_model=UserOutSchema, dependencies=[Depends(UserPermissions.CanCreateUsers)])
@invalidate_cache(tags=("users:list", "users:search"))
async def create_user(
    data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    user = await service.create(data)
    user = await service.get(user.id)
    return _to_user_out(user)


@router.get(
    "/search", response_model=list[UserOutSchema], dependencies=[Depends(UserPermissions.CanViewUsers)]
)
@cached(ttl=30, tags=("users:search",))
async def search_users(
    q: str,
    service: UserService = Depends(get_user_service),
    pagination: PaginationParamsSchema = Depends(),
):
    users = await service.search(q, pagination)
    return [_to_user_out(user) for user in users]


@router.get(
    "/{user_id}", response_model=UserOutSchema, dependencies=[Depends(UserPermissions.CanViewUsers)]
)
@cached(ttl=60, tags=("users:detail",))
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    user = await service.get(user_id)
    return _to_user_out(user)


@router.patch("/{user_id}", response_model=UserOutSchema)
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def update_user(
    user_id: uuid.UUID,
    data: AdminUserUpdateSchema,
    current_user: CurrentUserSchema = Depends(UserPermissions.CanManageUsers),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot modify yourself. Use /me")

    user = await service.admin_update(user_id, data)
    return _to_user_out(user)


@router.delete("/{user_id}")
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def archive_user(
    user_id: uuid.UUID,
    current_user: CurrentUserSchema = Depends(UserPermissions.CanDeleteUsers),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot delete yourself")

    await service.archive(user_id)
    return StatusResponse(status="archived", message="User archived successfully")


@router.post("/{user_id}/block")
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def block_user(
    user_id: uuid.UUID,
    current_user: CurrentUserSchema = Depends(UserPermissions.CanManageUsers),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot block yourself")

    await service.block(user_id)
    return StatusResponse(status="blocked", message="User blocked successfully")


@router.post("/{user_id}/activate")
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def activate_user(
    user_id: uuid.UUID,
    current_user: CurrentUserSchema = Depends(UserPermissions.CanManageUsers),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot activate yourself")

    await service.activate(user_id)
    return StatusResponse(status="active", message="User activated successfully")
