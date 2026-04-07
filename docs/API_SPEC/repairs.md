# 🔧 REPAIRS API SPEC

## 📌 Umumiy tavsif

`Repairs` — texnik vositalarni ta’mirlash jarayonini to‘liq boshqaradi.

Bu modul orqali:

* nosozliklar qayd etiladi
* ustalarga topshiriladi
* ta’mir jarayoni kuzatiladi
* xarajatlar hisoblanadi
* natija analiz qilinadi

---

# 🧠 PROCESS (FLOW)

1. 📢 Nosozlik aniqlanadi (`reported`)
2. 👨‍🔧 Ustaga biriktiriladi (`assigned`)
3. 🔄 Ta’mir jarayoni (`in_progress`)
4. ✅ Tugatildi (`done`) yoki ❌ bekor (`canceled`)

---

# 🔐 ACCESS CONTROL

| Role       | Access              |
| ---------- | ------------------- |
| superadmin | full                |
| admin      | full (scope ichida) |
| moderator  | create / update     |
| analyst    | read only           |

---

# 📦 ENTITY STRUCTURE (RESPONSE)

```json
{
  "id": "uuid",
  "asset": {
    "id": "uuid",
    "asset_tag": "INV-0001"
  },
  "status": "in_progress",
  "repair_type": "corrective",
  "description": "Hard disk ishlamayapti",
  "reported_by": {
    "id": "uuid",
    "name": "Ali Valiyev"
  },
  "assigned_to": {
    "id": "uuid",
    "name": "Usta Karim"
  },
  "performed_by": {
    "id": "uuid",
    "name": "Usta Karim"
  },
  "reported_at": "timestamp",
  "repair_date": "timestamp",
  "downtime_hours": 12,
  "total_cost": 150.00,
  "created_at": "timestamp"
}
```

---

# 🚀 ENDPOINTS

---

## 1. CREATE REPAIR REQUEST

### POST `/api/v1/repairs`

### Request

```json
{
  "asset_id": "uuid",
  "description": "Kompyuter yoqilmayapti"
}
```

---

### Logic

* status = `reported`
* reported_by = current user
* asset status → `broken`

---

### Response

```json
{
  "id": "uuid",
  "message": "Repair created"
}
```

---

## 2. ASSIGN REPAIR

### POST `/api/v1/repairs/{id}/assign`

```json
{
  "assigned_to": "uuid"
}
```

---

### Logic

* status → `in_progress`

---

## 3. UPDATE REPAIR STATUS

### POST `/api/v1/repairs/{id}/status`

```json
{
  "status": "done"
}
```

---

### Logic

* history yoziladi (`repair_status_history`)
* agar `done`:

  * asset.status → `active`
  * asset.last_repair_date update
  * asset.failure_count +1

---

## 4. ADD USED PARTS

### POST `/api/v1/repairs/{id}/parts`

```json
{
  "part_id": "uuid",
  "quantity": 2,
  "cost": 50
}
```

---

### Logic

* `repair_parts` ga yoziladi
* warehouse’dan kamayadi
* total_cost update qilinadi

---

## 5. COMPLETE REPAIR

### POST `/api/v1/repairs/{id}/complete`

```json
{
  "repair_date": "timestamp",
  "downtime_hours": 10
}
```

---

## 6. GET REPAIRS LIST

### GET `/api/v1/repairs`

### Filters

```
status
region_id
service_id
date_from
date_to
```

---

## 7. GET SINGLE REPAIR

### GET `/api/v1/repairs/{id}`

---

# 🔗 RELATIONSHIPS

| Field        | Table  |
| ------------ | ------ |
| asset_id     | assets |
| reported_by  | users  |
| assigned_to  | users  |
| performed_by | users  |

---

# ⚠️ BUSINESS RULES

1. ❌ Bir assetda bir vaqtning o‘zida 2 ta active repair bo‘lmasin
2. ❌ `done` bo‘lgan repair o‘zgartirilmaydi
3. ✅ Har status o‘zgarishi history’ga yoziladi
4. ✅ Har part ishlatilganda warehouse update bo‘ladi

---

# 📊 ANALYTICS HOOKS

Har repair:

* downtime_hours → KPI
* total_cost → expense
* failure_count → reliability

---

# 🔐 SECURITY

* faqat assigned user update qila oladi
* admin override qila oladi
* audit_logs yoziladi

---

# 📎 ATTACHMENTS

### POST `/api/v1/repairs/{id}/attachments`

* foto
* pdf (akt, hujjat)
* video

---

# 🧠 BACKEND IMPLEMENTATION

Service layer:

* create_repair()
* assign_repair()
* complete_repair()

Event driven:

* repair_created → audit
* repair_done → analytics update

---

# 🚀 FUTURE

* external repair (chet davlat)
* SLA tracking
* AI failure prediction
