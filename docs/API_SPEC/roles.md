# 🔐 ROLES API SPEC

## 📌 Umumiy tavsif

`Roles` — tizimdagi foydalanuvchilarning vakolat darajasini belgilaydi.

Har bir role:

* qaysi amalni bajarishi mumkinligini aniqlaydi
* permissions orqali kengaytiriladi
* security va audit uchun asos bo‘ladi

---

# 🧠 CORE CONCEPT

👉 System RBAC (Role-Based Access Control) asosida ishlaydi:

```
User → Role → Permissions
```

---

## Default roles

| Role       | Tavsif                          |
| ---------- | ------------------------------- |
| superadmin | To‘liq nazorat                  |
| admin      | Hudud / xizmat ichida boshqaruv |
| moderator  | Operatsion ishlar               |
| analyst    | Faqat analytics                 |

---

# 🔐 ACCESS CONTROL

| Action      | superadmin | admin | moderator | analyst |
| ----------- | ---------- | ----- | --------- | ------- |
| create role | ✅          | ❌     | ❌         | ❌       |
| update role | ✅          | ❌     | ❌         | ❌       |
| delete role | ✅          | ❌     | ❌         | ❌       |
| view roles  | ✅          | ✅     | ❌         | ❌       |

---

# 📦 ENTITY STRUCTURE

```json id="0c0y6y"
{
  "id": "uuid",
  "name": "admin",
  "description": "Hudud administrator",
  "permissions": [
    {
      "code": "assets.read"
    },
    {
      "code": "assets.create"
    }
  ]
}
```

---

# 🚀 ENDPOINTS

---

## 1. CREATE ROLE

### POST `/api/v1/roles`

### Request

```json id="5o9e1z"
{
  "name": "warehouse_manager",
  "description": "Ombor boshqaruvchisi"
}
```

---

### Logic

* role yaratiladi
* permissions keyin biriktiriladi

---

## 2. GET ROLES

### GET `/api/v1/roles`

---

### Response

```json id="l0dzn6"
[
  {
    "id": "uuid",
    "name": "admin",
    "description": "Admin role"
  }
]
```

---

## 3. GET ROLE BY ID

### GET `/api/v1/roles/{id}`

---

## 4. UPDATE ROLE

### PATCH `/api/v1/roles/{id}`

```json id="r1mfcz"
{
  "description": "Updated description"
}
```

---

## 5. DELETE ROLE

### DELETE `/api/v1/roles/{id}`

---

### ⚠️ Logic

* ❌ agar role userlarga biriktirilgan bo‘lsa → delete mumkin emas

---

# 🔗 ROLE ↔ PERMISSIONS

---

## 6. ASSIGN PERMISSIONS

### POST `/api/v1/roles/{id}/permissions`

```json id="1x3l2y"
{
  "permissions": [
    "assets.read",
    "assets.create",
    "repairs.update"
  ]
}
```

---

### Logic

* `role_permissions` jadvaliga yoziladi
* eski permissions replace qilinadi

---

## 7. GET ROLE PERMISSIONS

### GET `/api/v1/roles/{id}/permissions`

---

# ⚠️ BUSINESS RULES

1. ❌ `superadmin` role o‘chirib bo‘lmaydi
2. ❌ `superadmin` permissionlari o‘zgartirilmaydi
3. ❌ role nomi UNIQUE bo‘lishi kerak
4. ❌ role delete qilishdan oldin userlar tekshiriladi

---

# 🔐 SECURITY

* faqat superadmin role’larni boshqaradi
* barcha o‘zgarishlar audit_logs ga yoziladi

---

# 📊 ANALYTICS HOOKS

* kim qaysi role bilan ishlayapti
* access misuse monitoring

---

# 🧠 BACKEND IMPLEMENTATION

Service layer:

* create_role()
* update_role()
* assign_permissions()
* delete_role()

---

# 🚀 FUTURE

* dynamic roles (UI orqali)
* permission templates
