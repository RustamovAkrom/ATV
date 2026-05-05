# API Schema & Endpoints Audit Report

**Audit Date**: May 1, 2026
**Workspace**: e:\IIB ATV

---

## Executive Summary

Found **18 major issues** across the API:
- **9 DELETE endpoints** without `response_model` definitions
- **9 POST/DELETE endpoints** returning untyped dicts (`{"status": "..."}`) without response schema
- **Mixed pagination patterns** (page-based vs hardcoded limit/offset)
- **Inconsistent status codes** (POST returning 200 instead of 201)
- **Missing response models** on state-change POST endpoints
- **No error responses documented** in route decorators

---

## Issue 1: DELETE Endpoints Without response_model (CRITICAL)

These endpoints return dict literals but have no `response_model` defined. FastAPI will pass through unvalidated responses.

| File | Line | Endpoint | Issue |
|------|------|----------|-------|
| [src/api/v1/assets/asset_categories.py](src/api/v1/assets/asset_categories.py#L30) | 30-36 | `DELETE /{category_id}` | No response_model; returns `{"status": "deleted"}` |
| [src/api/v1/assets/asset_classes.py](src/api/v1/assets/asset_classes.py#L25) | 25-31 | `DELETE /{class_id}` | No response_model; returns `{"status": "deleted"}` |
| [src/api/v1/assets/asset_model.py](src/api/v1/assets/asset_model.py#L24) | 24-30 | `DELETE /{model_id}` | Returns result of service.delete() (likely raw model or void) |
| [src/api/v1/assets/manufacturer.py](src/api/v1/assets/manufacturer.py#L27) | 27-33 | `DELETE /{manufacturer_id}` | No response_model; returns `{"status": "deleted"}` |
| [src/api/v1/assets/asset_documents.py](src/api/v1/assets/asset_documents.py#L47) | 47-58 | `DELETE /{document_id}` | No response_model; returns `{"status": "deleted"}` |
| [src/api/v1/assets/asset.py](src/api/v1/assets/asset.py#L182) | 182-190 | `DELETE /{asset_id}` | No response_model; returns `{"status": "deleted"}` |
| [src/api/v1/rbac/rbac.py](src/api/v1/rbac/rbac.py#L66) | 66-73 | `DELETE /roles/{role_id}` | No response_model; returns `{"status": "deleted"}` |
| [src/api/v1/users/user.py](src/api/v1/users/user.py#L146) | 146-157 | `DELETE /{user_id}` | No response_model; returns `{"status": "archived"}` |

**Fix**: Define `response_model=StatusResponse` for all DELETE endpoints (or create appropriate schema like `DeletedResponse`).

---

## Issue 2: POST/State-Change Endpoints Without response_model

These endpoints lack `response_model` definitions but return untyped dicts.

| File | Line | Endpoint | Issue |
|------|------|----------|-------|
| [src/api/v1/users/user.py](src/api/v1/users/user.py#L68) | 68-80 | `POST /me/change-password` | No response_model; returns `{"status": "ok"}` |
| [src/api/v1/users/user.py](src/api/v1/users/user.py#L160) | 160-171 | `POST /{user_id}/block` | No response_model; returns `{"status": "blocked"}` |
| [src/api/v1/users/user.py](src/api/v1/users/user.py#L174) | 174-185 | `POST /{user_id}/activate` | No response_model; returns `{"status": "active"}` |
| [src/api/v1/auth/auth.py](src/api/v1/auth/auth.py#L65) | 65-77 | `POST /logout` | No response_model; returns `{"status": "ok"}` |
| [src/api/v1/auth/auth.py](src/api/v1/auth/auth.py#L80) | 80-89 | `POST /logout-all` | No response_model; returns `{"status": "ok"}` |
| [src/api/v1/auth/sessions.py](src/api/v1/auth/sessions.py#L24) | 24-31 | `DELETE /{session_id}` | Has status_code but no response_model; returns `{"status": "Session revoked"}` |
| [src/api/v1/auth/sessions.py](src/api/v1/auth/sessions.py#L34) | 34-40 | `POST /logout-all` | Has status_code but no response_model; returns `{"detail": "All sessions revoked"}` |
| [src/api/v1/auth/sessions.py](src/api/v1/auth/sessions.py#L43) | 43-52 | `POST /cleanup` | Has status_code but no response_model; returns `{"deleted": deleted}` |
| [src/api/v1/notifications.py](src/api/v1/notifications.py#L59) | 59-66 | `POST /{notification_id}/read` | No response_model; returns `{"status": "ok"}` |
| [src/api/v1/notifications.py](src/api/v1/notifications.py#L69) | 69-75 | `POST /read-all` | No response_model; returns `{"status": "ok"}` |

**Fix**: Add `response_model=StatusResponse` to these endpoints.

---

## Issue 3: Inconsistent Response Schemas for State Changes

**Problem**: Similar operations return different response shapes:
- `sessions.py` line 40: Returns `{"detail": "..."}` (non-standard)
- `sessions.py` line 52: Returns `{"deleted": count}` (inconsistent key)
- `notifications.py` line 84: Returns `{"count": count}` (non-standard)

**Expected**: All state-change operations should return consistent `StatusResponse` or have specific typed schemas.

---

## Issue 4: Pagination Inconsistencies

### Pattern A: Page-based pagination (Standard)
- Uses `PaginationParamsSchema` with `page` and `limit`
- Examples: [src/api/v1/audit/audit.py](src/api/v1/audit/audit.py#L13), [src/api/v1/approvals/approvals.py](src/api/v1/approvals/approvals.py#L20)

### Pattern B: Hardcoded limit/offset (Inconsistent)
- [src/api/v1/notifications.py](src/api/v1/notifications.py#L45-L52) line 51:
  ```python
  return await service.list_by_user(
      user_id=current_user.id,
      is_read=is_read,
      limit=50,      # ← Hardcoded
      offset=0,      # ← Hardcoded
  )
  ```

### Pattern C: Custom pagination dependency
- [src/api/v1/approvals/approvals.py](src/api/v1/approvals/approvals.py#L20) line 20:
  ```python
  pagination: PaginationParamsSchema = Depends(get_pagination)
  ```
  Uses `get_pagination` from [src/api/dependencies/paginations.py](src/api/dependencies/paginations.py) instead of direct Depends()

**Issue**: Inconsistent pagination handling makes API unpredictable for clients.

**Fix**: Standardize to one pattern - recommend removing `get_pagination` wrapper and using direct `Depends()` on all endpoints.

---

## Issue 5: Status Code Inconsistencies

### POST endpoints returning 200 instead of 201
- [src/api/v1/users/security.py](src/api/v1/users/security.py#L16) line 16: `status_code=status.HTTP_200_OK` (should be 201 for password reset)
- [src/api/v1/users/security.py](src/api/v1/users/security.py#L35) line 35: `status_code=status.HTTP_200_OK` (should be 200, this is okay)

### DELETE endpoints inconsistently using status_code
- [src/api/v1/auth/sessions.py](src/api/v1/auth/sessions.py#L24) line 24: Has `status_code=status.HTTP_200_OK` (DELETE should return 204 No Content or 200 with response)
- [src/api/v1/auth/sessions.py](src/api/v1/auth/sessions.py#L34) line 34: `POST /logout-all` also returns 200

**Fix**: Use HTTP 201 for POST endpoints that create resources, 200 for state changes, 204 for DELETE endpoints with no response body.

---

## Issue 6: Missing response_model with Mismatch Between Declaration and Return

### Notification service: Hardcoded pagination vs response_model
- [src/api/v1/notifications.py](src/api/v1/notifications.py#L45):
  ```python
  @router.get("/", response_model=list[NotificationSchema])
  async def get_notifications(...):
      return await service.list_by_user(
          limit=50,      # ← Hardcoded, not from request
          offset=0,      # ← Not paginated by client
      )
  ```
  **Issue**: Response is a flat list but should be paginated. Consider returning `PageOutSchema[NotificationSchema]`.

---

## Issue 7: No Error Response Documentation

None of the endpoints have documented error responses using the `responses` parameter. Example missing:

```python
@router.get(
    "/",
    response_model=list[UserOutSchema],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"}
    }
)
```

**Current state**: All endpoints lack error response schemas.

---

## Issue 8: Untyped Response Filtering/Queries (No validation)

### Audit service: query parameters with validation
- [src/api/v1/audit/audit.py](src/api/v1/audit/audit.py#L24) line 24: `status_code: int | None = Query(None, ge=100, le=599)` ✓ Good validation

### Asset analytics: datetime parsing but type mismatches
- [src/api/v1/analytics/assignment_analytics.py](src/api/v1/analytics/assignment_analytics.py#L50) line 50-51:
  ```python
  date_from: str | None = Query(None, description="ISO format datetime")
  date_to: str | None = Query(None, description="ISO format datetime")
  ```
  **Issue**: Accepts strings, manually parsed, could fail at runtime. Should use `datetime | None = Query(None)` with Pydantic parsing.

---

## Issue 9: Service Return Types

### Raw Model Returns (Potential type mismatches)
Services return raw ORM models instead of schemas in many cases:
- [src/api/v1/assets/asset.py](src/api/v1/assets/asset.py#L84) returns result of `service.list()`
- [src/api/v1/rbac/rbac.py](src/api/v1/rbac/rbac.py#L31) returns result of `service.list_roles()`
- [src/api/v1/rbac/rbac.py](src/api/v1/rbac/rbac.py#L40) returns result of `service.list_permissions()`

These services convert internally (good), but endpoint signatures don't reflect actual return types. The response_model should match what service actually returns.

---

## Issue 10: Validation Issues in Pydantic Schemas

### UserOutSchema missing required field default
[src/schemas/users/users.py](src/schemas/users/users.py#L36):
```python
class UserOutSchema(BaseModel):
    role: str              # ← Should be str | None (users can have no role)
    status: UserStatus     # ← Should validate against enum
```

**Current behavior**: Will fail validation if user has null role.

---

## Issue 11: ConfigDict usage inconsistency

### Missing ConfigDict in some schemas:
[src/schemas/common.py](src/schemas/common.py):
```python
class StatusResponse(BaseModel):
    status: str
    message: str | None
    # Missing: model_config = ConfigDict(from_attributes=True)
```

Many other schemas have this, but StatusResponse doesn't. Inconsistent ORM integration.

---

## Issue 12: Response Models Using PageSchema vs PageOutSchema

Inconsistent pagination response schemas:
- [src/api/v1/audit/audit.py](src/api/v1/audit/audit.py#L46): Uses `PageSchema[AuditSchema]` (minimal fields)
- [src/api/v1/approvals/approvals.py](src/api/v1/approvals/approvals.py#L22): Uses `PageOutSchema[ApprovalSchema]` (has `pages`, `has_next`, `has_prev`)

**Issue**: Clients can't rely on consistent pagination response structure.

---

## Summary Table: All Issues by Category

| Category | Count | Severity |
|----------|-------|----------|
| Missing response_model on DELETE | 8 | HIGH |
| Missing response_model on POST | 9 | HIGH |
| Pagination inconsistencies | 3 | MEDIUM |
| Status code inconsistencies | 3 | MEDIUM |
| Error responses not documented | ALL | LOW |
| Type validation issues | 2 | MEDIUM |
| ConfigDict inconsistency | 1 | LOW |
| Raw model returns | 3 | MEDIUM |

---

## Recommended Fixes (Priority Order)

### P0: CRITICAL (Fix immediately)
1. Add `response_model=StatusResponse` to all 17 DELETE/POST endpoints returning dicts
2. Define a dedicated delete response schema if different from StatusResponse
3. Standardize pagination pattern across all endpoints

### P1: IMPORTANT
1. Add `status_code` to POST endpoints (201 for creates, 200 for state changes)
2. Document error responses with `responses={}` parameter
3. Standardize between `PageSchema` and `PageOutSchema`

### P2: SHOULD DO
1. Fix UserOutSchema to allow null roles
2. Use Pydantic datetime parsing instead of manual string parsing
3. Add ConfigDict to StatusResponse
4. Type service return values explicitly

### P3: NICE TO HAVE
1. Add comprehensive error response documentation
2. Create consistent response wrappers for all operations

---

## Files Requiring Changes

### High Priority (Multiple issues each)
- [src/api/v1/assets/asset.py](src/api/v1/assets/asset.py) - DELETE, status codes
- [src/api/v1/users/user.py](src/api/v1/users/user.py) - DELETE, POST response models, schema
- [src/api/v1/auth/auth.py](src/api/v1/auth/auth.py) - POST response models
- [src/api/v1/auth/sessions.py](src/api/v1/auth/sessions.py) - DELETE response models

### Medium Priority
- [src/api/v1/notifications.py](src/api/v1/notifications.py) - pagination, response models
- [src/api/v1/audit/audit.py](src/api/v1/audit/audit.py) - pagination response model
- [src/api/v1/approvals/approvals.py](src/api/v1/approvals/approvals.py) - pagination pattern
- [src/api/v1/analytics/assignment_analytics.py](src/api/v1/analytics/assignment_analytics.py) - datetime parsing
- [src/schemas/users/users.py](src/schemas/users/users.py) - schema validation

### All Asset Category Files
- [src/api/v1/assets/asset_categories.py](src/api/v1/assets/asset_categories.py) - line 30
- [src/api/v1/assets/asset_classes.py](src/api/v1/assets/asset_classes.py) - line 25
- [src/api/v1/assets/asset_model.py](src/api/v1/assets/asset_model.py) - line 24
- [src/api/v1/assets/manufacturer.py](src/api/v1/assets/manufacturer.py) - line 27
- [src/api/v1/assets/asset_documents.py](src/api/v1/assets/asset_documents.py) - line 47
- [src/api/v1/rbac/rbac.py](src/api/v1/rbac/rbac.py) - line 66
- [src/api/v1/users/security.py](src/api/v1/users/security.py) - lines 16, 35
- [src/schemas/common.py](src/schemas/common.py) - schema config

