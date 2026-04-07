# 📦 ASSETS API SPEC

## 📌 Umumiy tavsif

`Assets` — bu tizimdagi barcha texnik vositalarning asosiy jadvali.

Har bir texnika:

* qayerda joylashgan
* qaysi xizmatga tegishli
* holati qanday
* kim mas’ul

👉 hammasi shu modul orqali boshqariladi.

---

# 🧠 DATA SOURCE (QAYERDAN KELADI)

Asset yaratiladi:

1. 🏭 Xarid qilinganda
2. 📦 Ombordan chiqarilganda
3. 🔧 Yig‘ilganda (parts orqali)

---

# 🔐 ACCESS CONTROL

| Role       | Access                 |
| ---------- | ---------------------- |
| superadmin | full                   |
| admin      | CRUD (o‘z hududi)      |
| moderator  | read / update (status) |
| analyst    | read only              |

---

# 📦 ENTITY STRUCTURE (RESPONSE)

```json
{
  "id": "uuid",
  "asset_tag": "INV-0001",
  "serial_number": "SN123456",
  "model": {
    "id": "uuid",
    "name": "Lenovo ThinkPad T480"
  },
  "category": {
    "id": "uuid",
    "name": "Laptop"
  },
  "region": {
    "id": "uuid",
    "name": "Toshkent"
  },
  "service": {
    "id": "uuid",
    "name": "Tergov"
  },
  "status": "active",
  "lifecycle_stage": "normal",
  "condition_percent": 85,
  "last_repair_date": "2025-01-10",
  "failure_count": 2,
  "usage_intensity": 1200,
  "purchase_date": "2023-01-01",
  "purchase_cost": 1200.50,
  "responsible_user": {
    "id": "uuid",
    "full_name": "Ali Valiyev"
  },
  "created_at": "timestamp"
}
```

---

# 🚀 ENDPOINTS

---

## 1. CREATE ASSET

### POST `/api/v1/assets`

### Request

```json
{
  "model_id": "uuid",
  "serial_number": "SN123456",
  "asset_tag": "INV-0001",
  "region_id": "uuid",
  "service_id": "uuid",
  "purchase_date": "2023-01-01",
  "purchase_cost": 1200.50
}
```

### Response

```json
{
  "id": "uuid",
  "message": "Asset created successfully"
}
```

---

## 2. GET ASSETS LIST (FILTERABLE)

### GET `/api/v1/assets`

### Query params

```
region_id
service_id
status
category_id
search
page
limit
```

---

### Response

```json
{
  "total": 1200,
  "items": [...]
}
```

---

## 3. GET SINGLE ASSET

### GET `/api/v1/assets/{id}`

---

## 4. UPDATE ASSET

### PATCH `/api/v1/assets/{id}`

### Request

```json
{
  "status": "broken",
  "condition_percent": 40
}
```

---

## 5. DELETE (SOFT DELETE)

### DELETE `/api/v1/assets/{id}`

---

# 🔁 BUSINESS OPERATIONS (MUHIM)

---

## 6. TRANSFER ASSET

### POST `/api/v1/assets/{id}/transfer`

```json
{
  "to_region_id": "uuid",
  "to_service_id": "uuid"
}
```

👉 `asset_transfers` ga yoziladi

---

## 7. CHANGE STATUS

### POST `/api/v1/assets/{id}/status`

```json
{
  "status": "in_repair"
}
```

👉 `asset_state_history` ga yoziladi

---

## 8. ASSIGN RESPONSIBLE USER

### POST `/api/v1/assets/{id}/assign`

```json
{
  "user_id": "uuid"
}
```

---

## 9. MOVE TO WAREHOUSE

### POST `/api/v1/assets/{id}/warehouse`

```json
{
  "warehouse_id": "uuid"
}
```

---

# 📊 VALIDATIONS

* `serial_number` UNIQUE
* `asset_tag` UNIQUE
* `condition_percent` → 0–100
* `status` → ENUM (asset_statuses)

---

# ⚠️ BUSINESS RULES

1. ❌ Agar `is_transfer_locked = true` → transfer mumkin emas
2. ❌ Agar `status = disposed` → update mumkin emas
3. ✅ Har status o‘zgarishi history’ga yoziladi
4. ✅ Har transfer log qilinadi

---

# 🔗 RELATIONSHIPS

| Field               | Table        |
| ------------------- | ------------ |
| model_id            | asset_models |
| region_id           | regions      |
| service_id          | services     |
| responsible_user_id | users        |

---

# 🧠 BACKEND IMPLEMENTATION NOTES

* service layer → business logic
* repository → DB access
* event → audit + analytics trigger

---

# 🚀 FUTURE

* barcode / QR scan
* IoT integration
* auto failure detection
