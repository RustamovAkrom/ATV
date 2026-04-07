# 🔑 PERMISSIONS API SPEC

## 📌 Umumiy tavsif

`Permissions` — tizimdagi har bir amalni (action) boshqaradi.

Role’lar faqat **permissionlar to‘plami** hisoblanadi.

---

# 🧠 CORE CONCEPT

```text id="r8d1k2"
User → Role → Permissions → Action
```

---

## Permission format

👉 har doim quyidagi formatda:

```text id="m2q9w7"
<resource>.<action>
```

---

## Misollar

```text id="7zj2n1"
assets.read
assets.create
assets.update
assets.delete

repairs.create
repairs.update

warehouse.stock.in
warehouse.stock.out

analytics.view
users.manage
```

---

# 🎯 PURPOSE

* granular access control
* xavfsizlik
* audit nazorati

---

# 🔐 ACCESS CONTROL

| Action            | superadmin | admin | moderator | analyst |
| ----------------- | ---------- | ----- | --------- | ------- |
| create permission | ❌ (manual) | ❌     | ❌         | ❌       |
| view permissions  | ✅          | ✅     | ❌         | ❌       |
| assign to role    | ✅          | ❌     | ❌         | ❌       |

---

# 📦 ENTITY STRUCTURE

```json id="k9w2m3"
{
  "id": "uuid",
  "code": "assets.read",
  "name": "Read assets",
  "description": "Allows viewing assets",
  "created_at": "timestamp"
}
```

---

# ⚠️ IMPORTANT DESIGN

👉 Permissionlar:

❌ runtime’da yaratilmaydi
❌ user tomonidan qo‘shilmaydi

✅ faqat developer tomonidan belgilanadi
✅ seed orqali DB ga yoziladi

---

# 🚀 ENDPOINTS

---

## 1. GET ALL PERMISSIONS

### GET `/api/v1/permissions`

---

### Response

```json id="c1x8a5"
[
  {
    "code": "assets.read",
    "name": "Read assets"
  },
  {
    "code": "repairs.update",
    "name": "Update repair"
  }
]
```

---

## 2. GET PERMISSION BY CODE

### GET `/api/v1/permissions/{code}`

---

# 🔗 RELATIONSHIPS

| Table            | Relation          |
| ---------------- | ----------------- |
| role_permissions | role ↔ permission |

---

# 🧠 PERMISSION GROUPING

👉 Frontend uchun qulaylik:

```json id="u8r2f0"
{
  "assets": [
    "assets.read",
    "assets.create"
  ],
  "repairs": [
    "repairs.create",
    "repairs.update"
  ]
}
```

---

# ⚠️ BUSINESS RULES

1. ❌ Permission o‘chirib bo‘lmaydi
2. ❌ Permission code UNIQUE
3. ❌ Permission o‘zgartirilmaydi (immutable)
4. ✅ Faqat role orqali assign qilinadi

---

# 🔐 SECURITY

* permissionlar hardcoded bo‘ladi
* audit_logs da role-permission o‘zgarishi yoziladi

---

# 🧠 BACKEND IMPLEMENTATION

---

## 🔹 1. Permission seeding

Startup paytida:

```python id="n5x2qp"
permissions = [
    "assets.read",
    "assets.create",
    "assets.update",
    "assets.delete",
    "repairs.create",
    "repairs.update",
    "analytics.view"
]
```

---

## 🔹 2. Middleware / Dependency

```python id="3l7k0z"
def require_permission(code: str):
    ...
```

---

## 🔹 3. Usage

```python id="z0w4ns"
@router.get("/assets")
@require_permission("assets.read")
```

---

# 📊 ANALYTICS HOOKS

* kim qaysi permission bilan ishlayapti
* xavfli amallar monitoringi

---

# 🚀 FUTURE

* permission UI manager
* dynamic permission groups
* ABAC (attribute-based access)

---

# 🏁 XULOSA

Bu modul:

✅ security asosini tashkil qiladi
✅ roles’ni moslashuvchan qiladi
✅ systemni scalable qiladi

---
