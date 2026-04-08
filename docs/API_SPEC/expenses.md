# 💰 EXPENSES API SPEC

## 📌 Umumiy tavsif

`Expenses` — tizimdagi barcha moliyaviy xarajatlarni hisobga oladi.

Bu modul orqali:

* texnika xarajatlari
* ta’mirlash xarajatlari
* xizmatlar bo‘yicha xarajatlar

nazorat qilinadi.

---

# 🧠 CORE CONCEPT

👉 Har bir xarajat quyidagiga bog‘lanadi:

```text id="expense-flow"
Asset / Repair / Region / Service
```

---

## Expense turlari

| Type        | Tavsif        |
| ----------- | ------------- |
| purchase    | xarid         |
| repair      | ta’mir        |
| maintenance | texnik xizmat |
| logistics   | tashish       |
| other       | boshqa        |

---

# 📦 ENTITY STRUCTURE

```json id="expense-response"
{
  "id": "uuid",
  "amount": 1500000,
  "currency": "UZS",
  "expense_type": "repair",
  "description": "Hard disk almashtirildi",
  "asset": {
    "id": "uuid",
    "asset_tag": "INV-001"
  },
  "repair": {
    "id": "uuid"
  },
  "region": {
    "id": "uuid",
    "name": "Toshkent"
  },
  "service": {
    "id": "uuid",
    "name": "IT"
  },
  "occurred_at": "timestamp",
  "created_by": "uuid",
  "file_url": "url"
}
```

---

# 🔐 ACCESS CONTROL

| Role       | Access      |
| ---------- | ----------- |
| superadmin | full        |
| admin      | create/read |
| moderator  | create      |
| analyst    | read        |

---

# 🚀 ENDPOINTS

---

## 1. CREATE EXPENSE

### POST `/api/v1/expenses`

```json id="create-expense"
{
  "amount": 500000,
  "expense_type": "repair",
  "asset_id": "uuid",
  "repair_id": "uuid",
  "region_id": "uuid",
  "service_id": "uuid",
  "description": "Ehtiyot qism almashtirildi",
  "occurred_at": "timestamp"
}
```

---

### ⚠️ Logic

* `expense_type` validatsiya qilinadi
* kamida bitta context bo‘lishi kerak:

  * asset yoki repair
* audit yoziladi

---

## 2. GET EXPENSES LIST

### GET `/api/v1/expenses`

### Query params

```text id="expense-filters"
region_id
service_id
asset_id
repair_id
expense_type
date_from
date_to
min_amount
max_amount
```

---

### Response

```json id="expenses-list"
{
  "total": 1000,
  "items": [...]
}
```

---

## 3. GET SINGLE EXPENSE

### GET `/api/v1/expenses/{id}`

---

## 4. UPDATE EXPENSE

### PATCH `/api/v1/expenses/{id}`

---

### ⚠️ Logic

* ❌ faqat superadmin update qila oladi
* audit yoziladi

---

## 5. DELETE EXPENSE

### DELETE `/api/v1/expenses/{id}`

---

### ⚠️ Logic

* soft delete tavsiya etiladi

---

# 📊 ANALYTICS ENDPOINTS

---

## 6. EXPENSES BY CATEGORY

### GET `/api/v1/expenses/analytics/by-category`

```json id="by-category"
[
  {
    "type": "repair",
    "total": 1000000
  }
]
```

---

---

## 7. EXPENSES BY REGION

### GET `/api/v1/expenses/analytics/by-region`

---

## 8. EXPENSES BY SERVICE

### GET `/api/v1/expenses/analytics/by-service`

---

## 9. EXPENSES OVER TIME

### GET `/api/v1/expenses/analytics/by-month`

---

# 🔗 RELATIONSHIPS

| Field      | Table    |
| ---------- | -------- |
| asset_id   | assets   |
| repair_id  | repairs  |
| region_id  | regions  |
| service_id | services |
| created_by | users    |

---

# ⚠️ BUSINESS RULES

1. ❌ amount > 0 bo‘lishi kerak
2. ❌ currency valid bo‘lishi kerak
3. ❌ expense_type majburiy
4. ✅ har expense audit qilinadi
5. ❌ duplicate transaction oldini olish (optional hash)

---

# 📎 ATTACHMENTS

👉 Xarajatga hujjat biriktiriladi:

* chek
* invoice
* akt

---

### Endpoint

POST `/api/v1/expenses/{id}/attachments`

---

# 🔐 SECURITY

* faqat authorized user create qila oladi
* barcha o‘zgarishlar audit_logs ga yoziladi
* region/service scope tekshiriladi

---

# 🧠 BACKEND IMPLEMENTATION

---

## 🔹 Expense service

* create_expense()
* validate_context()
* attach_file()

---

## 🔹 Analytics integration

* expenses → analytics_snapshots
* expenses → KPI

---

# 🚀 FUTURE

* budget limit
* automatic alerts
* anomaly detection

---

# 🏁 XULOSA

Bu modul:

✅ moliyaviy nazorat
✅ analytics asos
✅ rahbariyat qarorlariga ta’sir
✅ audit bilan bog‘liq

---
