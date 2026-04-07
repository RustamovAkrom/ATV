# USERS MODULE API SPEC

## 📌 Overview

Users moduli tizim foydalanuvchilarini boshqaradi.

⚠️ MUHIM QOIDA:

* Tizimga **oddiy ro‘yxatdan o‘tish (registration) YO‘Q**
* Foydalanuvchilar faqat:

  * **superadmin tomonidan yaratiladi**
* Har bir foydalanuvchi:

  * o‘ziga berilgan rol
  * hudud (region)
  * xizmat (service)
    doirasida ishlaydi

---

## 👥 ROLE MODEL

Tizimda asosiy rollar:

* **superadmin** — to‘liq nazorat
* **admin** — hudud darajasida boshqaruv
* **moderator** — operatsion ishlar
* **analyst** — faqat ko‘rish (read-only analytics)

---

## 🔐 ACCESS PRINCIPLES

* Har bir endpoint:

  * role orqali tekshiriladi
  * scope (region/service) orqali cheklanadi
* Hech bir user:

  * o‘zidan yuqori rolni boshqara olmaydi

---

# 👤 1. CREATE USER

## POST `/users`

### Purpose

Yangi foydalanuvchi yaratish (faqat superadmin yoki admin).

---

### Access

* superadmin
* admin (cheklangan)

---

### Request

```json
{
  "login": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "role_id": "uuid",
  "assigned_region_id": "uuid",
  "assigned_service_id": "uuid"
}
```

---

### Validation

* login unique bo‘lishi kerak
* password minimal security talablariga javob berishi kerak
* role mavjud bo‘lishi kerak
* region/service mos bo‘lishi kerak
* admin faqat o‘z scope ichida user yaratadi

---

### Response

```json
{
  "id": "uuid",
  "login": "string",
  "full_name": "string",
  "role": "moderator",
  "status": "active"
}
```

---

### DB Tables

* users
* roles
* regions
* services
* audit_logs

---

### Notes

* password hash qilinadi
* user default `active`
* audit yoziladi (USER_CREATED)
* userga login/password alohida beriladi

---

# 📋 2. GET USERS LIST

## GET `/users`

### Purpose

Foydalanuvchilar ro‘yxatini olish

---

### Access

* superadmin
* admin
* analyst (read-only)

---

### Query Params

* page
* size
* search
* role_id
* status
* region_id
* service_id

---

### Response

```json
{
  "items": [
    {
      "id": "uuid",
      "login": "user1",
      "full_name": "Ali Valiyev",
      "role": "admin",
      "status": "active"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 20
}
```

---

### Notes

* natija scope bo‘yicha filter qilinadi
* analyst faqat ko‘rish huquqiga ega

---

# 🔍 3. GET USER BY ID

## GET `/users/{id}`

### Purpose

Bitta foydalanuvchi ma’lumotlarini olish

---

### Access

* superadmin
* admin (faqat o‘z scope ichida)
* user o‘zi

---

### Response

```json
{
  "id": "uuid",
  "login": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "role": {
    "id": "uuid",
    "name": "admin"
  },
  "status": "active",
  "assigned_region_id": "uuid",
  "assigned_service_id": "uuid",
  "created_at": "datetime",
  "last_login_at": "datetime"
}
```

---

# ✏️ 4. UPDATE USER

## PATCH `/users/{id}`

### Purpose

Foydalanuvchi ma’lumotlarini yangilash

---

### Access

* superadmin
* admin (faqat o‘z scope ichida)

---

### Request

```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "role_id": "uuid",
  "assigned_region_id": "uuid",
  "assigned_service_id": "uuid"
}
```

---

### Validation

* role escalation taqiqlanadi
* scope dan tashqariga chiqish mumkin emas

---

### Notes

* audit yoziladi (USER_UPDATED)

---

# 🚫 5. CHANGE USER STATUS

## PATCH `/users/{id}/status`

### Purpose

Userni bloklash yoki aktiv qilish

---

### Access

* superadmin
* admin

---

### Request

```json
{
  "status": "active"
}
```

### Possible values

* active
* blocked
* archived

---

### Notes

* bloklangan user login qila olmaydi
* audit yoziladi (USER_STATUS_CHANGED)

---

# 🔑 6. PASSWORD RESET REQUEST

## POST `/users/{id}/password-request`

### Purpose

Foydalanuvchi parolini o‘zgartirish uchun ariza yuboradi

---

### Access

* user o‘zi

---

### Request

```json
{
  "reason": "string"
}
```

---

### DB Tables

* password_requests (yangi jadval kerak)
* audit_logs

---

### Notes

* status = pending
* audit yoziladi

---

# ✅ 7. APPROVE PASSWORD RESET

## POST `/users/{id}/password-approve`

### Purpose

Superadmin parol o‘zgartirishni tasdiqlaydi

---

### Access

* faqat superadmin

---

### Request

```json
{
  "new_password": "string"
}
```

---

### Validation

* request mavjud bo‘lishi kerak
* status = pending

---

### Response

```json
{
  "message": "Password updated"
}
```

---

### Notes

* password hash qilinadi
* request status = approved
* audit yoziladi (PASSWORD_RESET_APPROVED)

---

# 📎 8. USER ATTACHMENTS (HUJJATLAR)

## POST `/users/{id}/attachments`

### Purpose

Userga bog‘liq hujjatlarni yuklash (PDF, rasm va h.k.)

---

### Access

* admin
* superadmin

---

### Request (multipart)

* file
* description

---

### DB Tables

* attachments

---

### Notes

* hujjatlar davlat nazorati uchun saqlanadi
* entity_type = "user"

---

# 🔐 SECURITY & CONTROL

* userlar mustaqil yaratilmaydi
* barcha o‘zgarishlar audit qilinadi
* password reset faqat tasdiq bilan
* barcha ma’lumotlar davlat nazoratida
* har bir amal role orqali tekshiriladi

---

# 📌 SUMMARY

Users moduli:

* foydalanuvchilarni yaratadi va boshqaradi
* rollar orqali nazorat qiladi
* hudud va xizmat doirasini cheklaydi
* parolni faqat tasdiq bilan o‘zgartiradi
* barcha harakatlarni audit qiladi

Bu modul tizimdagi **barcha xavfsizlik va nazoratning asosiy qismi** hisoblanadi.
