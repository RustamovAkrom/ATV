# Enterprise RBAC + Permission System Documentation

## Overview

This document describes the comprehensive Role-Based Access Control (RBAC) and Permission system implemented in the FastAPI backend. It's designed for enterprise-grade applications with complex authorization requirements.

**Key Features:**
- ✅ Permission-based access control (not just roles)
- ✅ User-specific permission overrides
- ✅ Context-aware authorization (region/service scoping)
- ✅ Multi-level approval workflows
- ✅ Centralized permission registry
- ✅ Default role hierarchy with 9 roles

---

## Architecture

### Permission System Flow

```
User Request → CurrentUserSchema (has_permission check) →
  → Role Permissions + User Direct Permissions (aggregated) →
  → Guard/Dependency → Route Handler
```

### Core Components

1. **Permission Model** (`db.models.users.permission.Permission`)
   - Centralized definition of all system permissions
   - Code (unique): `"resource.action"` format
   - Name: Human-readable description
   - Example: `"asset.view"`, `"user.delete"`

2. **Role Model** (`db.models.users.permission.Role`)
   - Groups permissions together
   - Users assigned to one role per account
   - Many-to-many relationship with permissions

3. **User-Permission Relationship** (`user_permissions` table)
   - Allows users to have permissions beyond their role
   - Enables granular permission overrides
   - User has: Role permissions + Direct permissions

4. **CurrentUserSchema** (`schemas/auth.py`)
   - Runtime user context
   - Contains aggregated permissions
   - Methods: `has_permission()`, `has_role()`

5. **Permission Registry** (`core/security/rbac/permissions.py`)
   - Single source of truth for all permissions
   - Organized by resource (users, assets, approvals, etc.)
   - Auto-validated on startup

6. **Guards System** (`core/security/rbac/guards.py`)
   - `require_permission(...)` - Check permissions
   - `require_role(...)` - Check roles (less preferred)
   - FastAPI Depends integration

---

## Roles and Permissions

### Default Roles (9)

| Role | Purpose | Use Case |
|------|---------|----------|
| **SUPERADMIN** | Complete system access | System administrator |
| **ADMIN** | Full operational control | Operations manager |
| **MODERATOR** | Regional/operational management | Regional manager |
| **ANALYTIC** | Read-only analytics and audit | Analyst/Officer |
| **REGION_ADMIN** | Region-scoped management | Region administrator |
| **SERVICE_MANAGER** | Service-scoped operations | Service head |
| **OPERATOR** | Basic operational access | Field operator |
| **APPROVER** | Approval workflow focus | Approval authority |
| **AUDITOR** | Audit and compliance focus | Compliance officer |

### Permission Namespace

Permissions are organized by resource using dot notation:

```python
# Users & Profile
"users.view"
"users.create"
"users.edit"
"users.delete"

# RBAC
"roles.view"
"roles.manage"
"permissions.manage"

# Assets
"assets.view"
"assets.create"
"assets.update"
"assets.delete"
"assets.assign"
"assets.transfer"
"assets.archive"

# Approvals
"approvals.view"
"approvals.create"
"approvals.approve"
"approvals.reject"

# ... more in Permissions class
```

---

## How to Use

### 1. Permission-Based Endpoint Protection (RECOMMENDED)

```python
from fastapi import APIRouter, Depends
from core.security.rbac import presets
from core.security.auth.dependencies import get_current_user
from schemas.auth import CurrentUserSchema

router = APIRouter()

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    _: None = Depends(presets.CanDeleteUsers),  # Permission guard
):
    """Only users with 'users.delete' permission can delete."""
    await service.delete(user_id)
```

**Available Presets** (in `core/security/rbac/presets.py`):
- Users: `CanViewUsers`, `CanCreateUsers`, `CanManageUsers`, `CanDeleteUsers`
- Assets: `CanViewAssets`, `CanCreateAssets`, `CanUpdateAssets`, `CanDeleteAssets`
- Approvals: `CanViewApprovals`, `CanApproveApprovals`, `CanRejectApprovals`
- Audit: `CanViewAudit`, `CanExportAudit`
- RBAC: `CanManageRoles`
- And more...

### 2. Custom Permission Check

```python
@router.post("/critical-operation")
async def critical_operation(
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    # Check multiple permissions (all required)
    if not current_user.has_permission(
        "resource.create",
        "resource.approve"
    ):
        raise PermissionDenied("Missing required permissions")

    # Check if any permission exists (any_of=True)
    if not current_user.has_permission(
        "audit.view",
        "audit.export",
        any_of=True
    ):
        raise PermissionDenied("Need at least one permission")
```

### 3. Role-Based Guard (Less Preferred - Use Permission Guards Instead)

```python
from core.security.rbac.presets import IsAdmin

@router.get("/admin-panel")
async def admin_panel(_: None = Depends(IsAdmin)):
    """Only ADMIN and SUPERADMIN can access."""
```

---

## Context-Based Access Control

For region/service scoped authorization:

### Region-Scoped Access

```python
from core.security.access_control import AccessControl
from core.exceptions.errors import PermissionDenied

@router.get("/region/{region_id}/assets")
async def get_region_assets(
    region_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service = Depends(get_asset_service),
):
    # Ensure user can only access their assigned region
    AccessControl.check_region_access(current_user, region_id)

    return await service.list_by_region(region_id)
```

### Service-Scoped Access

```python
@router.post("/service/{service_id}/operate")
async def operate_service(
    service_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    # Ensure user can only manage their assigned service
    AccessControl.check_service_access(current_user, service_id)
```

### Creator-Only Access

```python
@router.patch("/resource/{resource_id}")
async def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service = Depends(get_resource_service),
):
    resource = await service.get(resource_id)

    # Only creator can modify (or SUPERADMIN)
    AccessControl.check_creator_access(current_user, resource.created_by_id)
```

---

## Approval Workflow Security

### Creator Cannot Approve Rule

The system enforces that the creator of an approval request **cannot** approve their own request:

```python
async def approve(
    self,
    approval_id: UUID,
    actor_id: UUID,
    comment: str | None = None
):
    approval = await self.approval_repo.get(approval_id)

    # Security: Creator cannot approve
    if approval.created_by_id == actor_id:
        raise PermissionDenied(
            "You cannot approve your own requests. "
            "Another authorized user must review."
        )

    # ... proceed with approval
```

**API Protection:**

```python
@router.post("/{approval_id}/approve", dependencies=[presets.CanApproveApprovals])
async def approve_approval(
    approval_id: UUID,
    data: ApprovalDecision,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    """
    Requires:
    - approvals.approve permission
    - User is NOT the creator (enforced in service)
    """
    return await service.approve(approval_id, current_user.id, data.comment)
```

---

## Adding New Permissions

### Step 1: Add to Permission Registry

In `src/core/security/rbac/permissions.py`:

```python
class Permissions:
    # --- NEW FEATURE ---
    FEATURE_VIEW = "feature.view"
    FEATURE_CREATE = "feature.create"
    FEATURE_MANAGE = "feature.manage"
```

### Step 2: Assign to Roles

In `src/core/security/rbac/permissions.py`:

```python
ROLE_PERMISSIONS: dict[str, set[str]] = {
    UserRole.ADMIN.value: ADMIN_BASE | {
        Permissions.FEATURE_VIEW,
        Permissions.FEATURE_CREATE,
        Permissions.FEATURE_MANAGE,
    },
    UserRole.OPERATOR.value: {
        Permissions.FEATURE_VIEW,
        Permissions.FEATURE_CREATE,
    },
}
```

### Step 3: Create Presets (Optional)

In `src/core/security/rbac/presets.py`:

```python
CanViewFeature = Depends(require_permission(Permissions.FEATURE_VIEW))
CanCreateFeature = Depends(require_permission(Permissions.FEATURE_CREATE))
CanManageFeature = Depends(require_permission(Permissions.FEATURE_MANAGE))
```

### Step 4: Use in Endpoints

```python
@router.get("/feature", dependencies=[presets.CanViewFeature])
async def list_feature():
    pass

@router.post("/feature", dependencies=[presets.CanCreateFeature])
async def create_feature():
    pass
```

---

## Adding New Roles

### Step 1: Add to UserRole Enum

In `src/db/models/enums.py`:

```python
class UserRole(StrEnum):
    # ... existing roles ...
    CUSTOM_ROLE = "custom_role"
```

### Step 2: Define Permissions for Role

In `src/core/security/rbac/permissions.py`:

```python
ROLE_PERMISSIONS: dict[str, set[str]] = {
    # ... existing mappings ...
    UserRole.CUSTOM_ROLE.value: {
        Permissions.ASSETS_VIEW,
        Permissions.REPAIRS_CREATE,
        Permissions.ANALYTICS_VIEW,
    },
}
```

### Step 3: Seed on Startup

The `seed_rbac()` function automatically:
- Creates the role (if not exists)
- Maps all defined permissions
- Is idempotent (safe to run multiple times)

---

## User-Specific Permission Overrides

### Grant Additional Permission to User

```python
# Get user from DB
user = await user_repo.get(user_id)

# Get permission from DB
perm = await perm_repo.get_by_code("asset.delete")

# Add direct permission
user.direct_permissions.append(perm)

# Save
await db.flush()

# Now user has this permission even if role doesn't include it
```

### Remove Permission from User

```python
user = await user_repo.get(user_id)

# Get permission to remove
perm = await perm_repo.get_by_code("asset.delete")

# Remove
user.direct_permissions.remove(perm)

await db.flush()
```

**Note:** This is useful for:
- Temporary elevation of privileges
- Exception handling
- Granular permission management

---

## Security Best Practices

### ✅ DO

1. **Use permission-based guards** instead of role checks
   ```python
   # Good
   dependencies=[presets.CanDeleteUsers]

   # Avoid
   dependencies=[presets.IsAdmin]
   ```

2. **Check creator access** for resource modifications
   ```python
   AccessControl.check_creator_access(user, resource.created_by_id)
   ```

3. **Enforce context access** for scoped operations
   ```python
   AccessControl.check_region_access(user, region_id)
   ```

4. **Aggregate permissions** in CurrentUserSchema
   - Role permissions + User permissions combined

5. **Use presets** for common checks
   - Reduces code duplication
   - Centralized management

### ❌ DON'T

1. **Hardcode role checks in endpoints**
   ```python
   # Bad
   if user.role == "admin":
       ...
   ```

2. **Skip permission checks** on "internal" endpoints
   - All endpoints need protection

3. **Trust user-provided role/permission data**
   - Always validate against database

4. **Allow creators to approve** their own requests
   - Enforced by approval service

5. **Forget region/service scoping**
   - Can lead to data leakage

---

## Testing Permissions

### Check User Has Permission

```python
user_schema = CurrentUserSchema(
    id=user.id,
    role="operator",
    permissions=["assets.view", "assets.create"]
)

# Check single permission
assert user_schema.has_permission("assets.view")

# Check multiple (all required)
assert user_schema.has_permission("assets.view", "assets.create")

# Check multiple (any required)
assert user_schema.has_permission(
    "assets.view",
    "assets.delete",
    any_of=True
)
```

### Test Endpoint Protection

```python
def test_delete_requires_permission():
    client = TestClient(app)

    # Get token with "operator" role (has assets.view, not assets.delete)
    token = get_token("operator")

    # Should fail
    response = client.delete(
        "/assets/123",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # PermissionDenied

    # Get token with "admin" role (has assets.delete)
    token = get_token("admin")

    # Should succeed
    response = client.delete(
        "/assets/123",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

---

## Endpoint Protection Summary

All endpoints are protected with permission guards:

| Resource | Permissions | Guard |
|----------|-------------|-------|
| Users | create, read, edit, delete | `CanViewUsers`, `CanCreateUsers`, etc. |
| Assets | view, create, update, delete, assign, transfer | `CanViewAssets`, `CanCreateAssets`, etc. |
| Approvals | view, create, approve, reject | `CanViewApprovals`, `CanApproveApprovals`, etc. |
| Audit | view, export | `CanViewAudit`, `CanExportAudit` |
| RBAC | manage | `CanManageRoles` |
| Repairs | view, create, update, complete | Covered by asset permissions |

---

## Database Schema

### Permissions Table
```sql
permissions:
  id (UUID) PRIMARY KEY
  code (VARCHAR UNIQUE) - "asset.view"
  name (VARCHAR UNIQUE) - "View Assets"
  description (TEXT)
  created_at, updated_at
```

### Roles Table
```sql
roles:
  id (UUID) PRIMARY KEY
  code (VARCHAR UNIQUE) - "admin"
  name (VARCHAR UNIQUE) - "Administrator"
  description (TEXT)
  created_at, updated_at
```

### Role-Permissions Relationship
```sql
role_permissions:
  role_id (FK)
  permission_id (FK)
  PRIMARY KEY (role_id, permission_id)
```

### User-Permissions Relationship (NEW)
```sql
user_permissions:
  user_id (FK)
  permission_id (FK)
  PRIMARY KEY (user_id, permission_id)
```

### Users Table (Existing)
```sql
users:
  id (UUID) PRIMARY KEY
  role_id (FK) - Single role per user
  assigned_region_id (FK) - For region scoping
  assigned_service_id (FK) - For service scoping
  ...
```

---

## Migration Guide

### From Old System (Hardcoded Permissions)

**Old:**
```python
if user.role == "admin":
    # allow operation
```

**New:**
```python
if not user.has_permission("resource.operation"):
    raise PermissionDenied()
```

### From Role-Only to Permission-Based

**Old:**
```python
@router.delete("/resource/{id}", dependencies=[presets.IsAdmin])
async def delete_resource(id: UUID):
    pass
```

**New:**
```python
@router.delete("/resource/{id}", dependencies=[presets.CanDeleteResource])
async def delete_resource(id: UUID):
    pass
```

---

## Troubleshooting

### User Cannot Access Endpoint

1. **Check permission:**
   ```python
   user = await db.get_user(user_id)
   print(user.permissions)  # Should include required permission
   ```

2. **Verify role mapping:**
   ```python
   role = await db.get_role(user.role_id)
   print(role.permissions)  # Should include permission
   ```

3. **Check direct permissions:**
   ```python
   print(user.direct_permissions)  # Any overrides?
   ```

### Permission Not Working After Creation

1. Ensure seed_rbac() was called on startup
2. Check that permission code matches exactly
3. Verify role mapping includes permission
4. Restart application (clear in-memory cache)

### How to Reset Permissions

```python
# Reseed all permissions and roles
async with db.session.begin():
    await seed_rbac(db.session)
```

---

## Contact & Support

For permission-related issues:
1. Check permission registry: `core/security/rbac/permissions.py`
2. Review role mappings: `ROLE_PERMISSIONS`
3. Check endpoint guards: `core/security/rbac/presets.py`
4. Review guards: `core/security/rbac/guards.py`
