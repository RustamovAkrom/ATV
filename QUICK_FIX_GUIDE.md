# Quick Fix Guide

## Critical Issues - Immediate Fixes Required

### Fix 1: Add StatusResponse to all DELETE endpoints

**Files to modify:**
1. `src/api/v1/assets/asset_categories.py` - line 30
2. `src/api/v1/assets/asset_classes.py` - line 25
3. `src/api/v1/assets/manufacturer.py` - line 27
4. `src/api/v1/assets/asset_documents.py` - line 47
5. `src/api/v1/assets/asset.py` - line 182
6. `src/api/v1/rbac/rbac.py` - line 66
7. `src/api/v1/users/user.py` - line 146
8. `src/api/v1/auth/sessions.py` - line 24

**Pattern:**

**Before:**
```python
@router.delete("/{resource_id}")
async def delete_resource(resource_id: UUID, ...):
    await service.delete(resource_id)
    return {"status": "deleted"}
```

**After:**
```python
@router.delete("/{resource_id}", response_model=StatusResponse)
async def delete_resource(resource_id: UUID, ...):
    await service.delete(resource_id)
    return StatusResponse(status="deleted", message=None)
    # OR
    return {"status": "deleted", "message": None}
```

---

### Fix 2: Add response_model to POST endpoints without responses

**Files to modify:**
1. `src/api/v1/users/user.py` - line 68, 160, 174
2. `src/api/v1/auth/auth.py` - line 65, 80
3. `src/api/v1/notifications.py` - line 59, 69

**Pattern:**

**Before:**
```python
@router.post("/me/change-password")
async def change_password(...):
    await service.change_password(...)
    return {"status": "ok"}
```

**After:**
```python
@router.post("/me/change-password", response_model=StatusResponse)
async def change_password(...):
    await service.change_password(...)
    return StatusResponse(status="ok", message="Password changed successfully")
    # OR
    return {"status": "ok", "message": "Password changed successfully"}
```

---

### Fix 3: Fix special cases with custom responses

#### Session cleanup endpoint - needs custom schema

**File:** `src/api/v1/auth/sessions.py` - line 43

**Before:**
```python
@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_sessions(...):
    deleted = await service.cleanup_expired()
    return {"deleted": deleted}
```

**After - Option A: Create new schema**

In `src/schemas/auth/security.py` or `src/schemas/users/sessions.py`:
```python
class CleanupResponse(BaseModel):
    deleted: int
    message: str = "Old sessions removed"
    model_config = ConfigDict(from_attributes=True)
```

Then in endpoint:
```python
@router.post("/cleanup", response_model=CleanupResponse, status_code=status.HTTP_200_OK)
async def cleanup_sessions(...):
    deleted = await service.cleanup_expired()
    return CleanupResponse(deleted=deleted)
```

**After - Option B: Use dict literal**
```python
@router.post("/cleanup", response_model=CleanupResponse, status_code=status.HTTP_200_OK)
async def cleanup_sessions(...):
    deleted = await service.cleanup_expired()
    return {"deleted": deleted, "message": "Old sessions removed"}
```

---

#### Notification unread count

**File:** `src/api/v1/notifications.py` - line 84

**Create schema in** `src/schemas/notifications/notification.py`:
```python
class UnreadCountResponse(BaseModel):
    count: int
    model_config = ConfigDict(from_attributes=True)
```

**Update endpoint:**
```python
@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(...):
    count = await service.get_unread_count(current_user.id)
    return UnreadCountResponse(count=count)
    # OR
    return {"count": count}
```

---

### Fix 4: Fix inconsistent session response fields

**File:** `src/api/v1/auth/sessions.py` - line 40

**Before:**
```python
@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all(...):
    await service.revoke_all(current_user.id)
    return {"detail": "All sessions revoked"}  # ← Wrong field name
```

**After:**
```python
@router.post("/logout-all", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def logout_all(...):
    await service.revoke_all(current_user.id)
    return StatusResponse(status="ok", message="All sessions revoked")
```

---

### Fix 5: Standardize pagination in notifications endpoint

**File:** `src/api/v1/notifications.py` - line 45-52

**Before:**
```python
@router.get("/", response_model=list[NotificationSchema])
async def get_notifications(
    is_read: bool | None = None,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list_by_user(
        user_id=current_user.id,
        is_read=is_read,
        limit=50,  # ← Hardcoded
        offset=0,  # ← Hardcoded
    )
```

**After - Option A: Proper pagination**
```python
from schemas.pagination import PageOutSchema

@router.get("/", response_model=PageOutSchema[NotificationSchema])
async def get_notifications(
    is_read: bool | None = None,
    pagination: PaginationParamsSchema = Depends(),
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list_by_user(
        user_id=current_user.id,
        is_read=is_read,
        pagination=pagination,  # Pass pagination object to service
    )
```

**After - Option B: If maintaining list response**
```python
@router.get("/", response_model=list[NotificationSchema])
async def get_notifications(
    is_read: bool | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list_by_user(
        user_id=current_user.id,
        is_read=is_read,
        limit=limit,
        offset=offset,
    )
```

---

### Fix 6: Fix UserOutSchema to allow null role

**File:** `src/schemas/users/users.py` - line 36

**Before:**
```python
class UserOutSchema(BaseModel):
    id: UUID
    login: str
    email: str
    phone: str
    role: str  # ← Non-optional, will fail if null
    permissions: list[str]
    first_name: str | None
    last_name: str | None
    status: UserStatus
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
```

**After:**
```python
class UserOutSchema(BaseModel):
    id: UUID
    login: str
    email: str
    phone: str
    role: str | None  # ← Allow null
    permissions: list[str] = Field(default_factory=list)
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
```

---

### Fix 7: Add ConfigDict to StatusResponse

**File:** `src/schemas/common.py`

**Before:**
```python
from pydantic import BaseModel

class StatusResponse(BaseModel):
    status: str
    message: str | None
```

**After:**
```python
from pydantic import BaseModel, ConfigDict

class StatusResponse(BaseModel):
    status: str
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)
```

---

### Fix 8: Fix asset_model.py DELETE to return typed response

**File:** `src/api/v1/assets/asset_model.py` - line 24

**Before:**
```python
@router.delete("/{model_id}")
async def delete_model(
    model_id: UUID,
    service: AssetModelService = Depends(get_asset_model_service),
):
    return await service.delete(model_id)  # ← Untyped return
```

**After:**
```python
@router.delete("/{model_id}", response_model=StatusResponse)
async def delete_model(
    model_id: UUID,
    service: AssetModelService = Depends(get_asset_model_service),
):
    await service.delete(model_id)
    return StatusResponse(status="deleted", message=None)
```

---

## Implementation Order

1. **Phase 1 (Critical - Do First):**
   - Add `response_model=StatusResponse` to all 17 DELETE/POST endpoints
   - Create 3 custom schemas (CleanupResponse, UnreadCountResponse, etc.)
   - Update imports in affected files

2. **Phase 2 (Important - Do Next):**
   - Fix UserOutSchema nullable fields
   - Add ConfigDict to StatusResponse
   - Standardize notification endpoint pagination

3. **Phase 3 (Should Do):**
   - Add error responses documentation
   - Add status codes (201 for POST creates)
   - Add comprehensive docstrings

4. **Phase 4 (Nice to Have):**
   - Replace manual datetime parsing with Pydantic types
   - Standardize PageSchema vs PageOutSchema usage

---

## Schema Files to Create/Update

### New Schemas to Add

**File:** `src/schemas/auth/security.py` (NEW ADDITIONS or create new file)
```python
from pydantic import BaseModel, ConfigDict

class CleanupResponse(BaseModel):
    deleted: int
    message: str = "Old sessions removed"
    model_config = ConfigDict(from_attributes=True)
```

**File:** `src/schemas/notifications/notification.py` (ADD TO EXISTING)
```python
class UnreadCountResponse(BaseModel):
    count: int
    model_config = ConfigDict(from_attributes=True)
```

---

## Testing After Fixes

Run FastAPI server and check:

```bash
# View OpenAPI schema
curl http://localhost:8000/openapi.json | jq '.paths'

# Specifically check for response_model on:
- POST /users/me/change-password
- DELETE /users/{user_id}
- DELETE /asset-categories/{category_id}
- POST /notifications/{notification_id}/read
- POST /auth/sessions/cleanup
```

---

## Verification Checklist

- [ ] All 17 endpoints have response_model defined
- [ ] StatusResponse has ConfigDict
- [ ] UserOutSchema allows null role
- [ ] Custom response schemas created and imported
- [ ] DELETE endpoints return 204 or have response schema
- [ ] POST endpoints have appropriate status codes
- [ ] All responses validate against schemas
- [ ] OpenAPI documentation updated correctly
- [ ] No untyped dict returns remain in routers
