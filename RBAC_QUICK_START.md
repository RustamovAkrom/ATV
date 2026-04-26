# RBAC Quick Start Guide

## 👉 For Developers: How to Protect an Endpoint

### 1. Simple Permission Check
```python
from fastapi import APIRouter, Depends
from core.security.rbac import presets

@router.delete("/resource/{id}")
async def delete_resource(
    id: UUID,
    _: None = Depends(presets.CanDeleteResource)  # ← Add guard
):
    pass
```

### 2. Multiple Permissions
```python
from core.security.rbac.guards import require_permission
from core.security.rbac.permissions import Permissions

@router.post("/critical")
async def critical_op(
    _: None = Depends(require_permission(
        Permissions.ASSETS_CREATE,
        Permissions.ASSETS_DELETE
    ))
):
    pass
```

### 3. Any Permission (OR logic)
```python
@router.get("/reports")
async def view_reports(
    _: None = Depends(require_permission(
        Permissions.ANALYTICS_VIEW,
        Permissions.AUDIT_VIEW,
        any_of=True  # ← User needs at least ONE
    ))
):
    pass
```

### 4. Context-Based Access
```python
from core.security.access_control import AccessControl

@router.get("/region/{region_id}")
async def get_region(
    region_id: UUID,
    current_user = Depends(get_current_user),
):
    # Ensure user only accesses their region
    AccessControl.check_region_access(current_user, region_id)
    return await service.get(region_id)
```

### 5. Creator-Only Access
```python
@router.delete("/resource/{id}")
async def delete_resource(
    id: UUID,
    current_user = Depends(get_current_user),
    service = Depends(get_service),
):
    resource = await service.get(id)

    # Only creator can delete
    AccessControl.check_creator_access(current_user, resource.created_by_id)

    await service.delete(id)
```

---

## 📋 Available Permission Presets

| Guard | Permission | Use Case |
|-------|-----------|----------|
| `CanViewUsers` | users.view | List/read users |
| `CanCreateUsers` | users.create | Create user |
| `CanDeleteUsers` | users.delete | Delete user |
| `CanViewAssets` | assets.view | List/read assets |
| `CanCreateAssets` | assets.create | Create asset |
| `CanDeleteAssets` | assets.delete | Delete asset |
| `CanViewApprovals` | approvals.view | List approvals |
| `CanApproveApprovals` | approvals.approve | Approve request |
| `CanViewAudit` | audit.view | View audit logs |
| `CanManageRoles` | roles.manage | Create/update roles |

### See All Available
File: `src/core/security/rbac/presets.py`

---

## 🔐 Default Roles & Permissions

| Role | Key Permissions | Best For |
|------|-----------------|----------|
| SUPERADMIN | ALL | System admin |
| ADMIN | Most (except cleanup) | Operations |
| MODERATOR | Regional ops | Regional managers |
| OPERATOR | Basic operations | Field staff |
| APPROVER | Approvals focus | Approval authorities |
| AUDITOR | Read-only + audit | Compliance |

---

## 🚀 Adding New Permission

### Step 1: Define Permission
```python
# src/core/security/rbac/permissions.py
class Permissions:
    FEATURE_VIEW = "feature.view"
    FEATURE_MANAGE = "feature.manage"
```

### Step 2: Assign to Roles
```python
ROLE_PERMISSIONS = {
    UserRole.ADMIN.value: {...} | {
        Permissions.FEATURE_VIEW,
        Permissions.FEATURE_MANAGE,
    },
}
```

### Step 3: Create Preset (Optional)
```python
# src/core/security/rbac/presets.py
CanViewFeature = Depends(require_permission(Permissions.FEATURE_VIEW))
CanManageFeature = Depends(require_permission(Permissions.FEATURE_MANAGE))
```

### Step 4: Use in Endpoint
```python
@router.get("/feature", dependencies=[presets.CanViewFeature])
async def list_feature():
    pass
```

---

## 🔄 System Flow

```
Request
  ↓
JWT decode → get_current_user()
  ↓
Load User from DB (role + permissions eager loaded)
  ↓
Create CurrentUserSchema(
    id=user.id,
    role=user.role.code,
    permissions=user.permissions  ← AGGREGATED!
)
  ↓
Endpoint guard checks: has_permission(...)
  ↓
Request context: request.state.user = CurrentUserSchema
  ↓
Endpoint handler executes
```

---

## ❌ Permission Denied

User gets 403 Forbidden when:
- Missing required permission
- Creator trying to approve own request
- Crossing region/service boundaries
- Insufficient role

Example Response:
```json
{
  "detail": "Missing required permissions",
  "error_code": "PERMISSION_DENIED"
}
```

---

## 🔍 Debug: Check User Permissions

```python
# Get user's permissions
user = await user_repo.get(user_id)
print(f"Permissions: {user.permissions}")
print(f"Role: {user.role.code}")
print(f"Direct: {[p.code for p in user.direct_permissions]}")

# Check specific permission
if user.has_permission("asset.delete"):
    print("Can delete assets")
```

---

## 🛑 Common Mistakes

### ❌ Hardcoded Role Check
```python
if user.role == "admin":  # DON'T!
    await service.delete()
```

### ✅ Use Permission Guard
```python
@router.delete(dependencies=[presets.CanDeleteAssets])  # DO!
async def delete():
    await service.delete()
```

---

## 📚 Full Documentation

See [RBAC_DOCUMENTATION.md](./RBAC_DOCUMENTATION.md) for:
- Complete architecture overview
- All permission namespaces
- Adding new roles
- User permission overrides
- Context-based access control
- Approval workflow rules
- Testing patterns
- Troubleshooting

---

## 🎯 One More Thing

The system automatically creates all default roles and permissions on startup.

**Migration from old system:**
- Old role checks still work (backward compatible)
- But use permission guards going forward
- Gradual migration OK

---

**Quick Links:**
- Permissions: `src/core/security/rbac/permissions.py`
- Presets: `src/core/security/rbac/presets.py`
- Guards: `src/core/security/rbac/guards.py`
- Access Control: `src/core/security/access_control.py`
- Models: `src/db/models/users/permission.py`, `user.py`
