# AUTH MODULE API SPEC

## 📌 Overview

Auth moduli foydalanuvchilarni:

* tizimga kiritish (login)
* sessiyani boshqarish
* tokenlarni yangilash
* xavfsizlikni nazorat qilish

uchun ishlatiladi.

Bu modul **JWT (access + refresh token)** asosida ishlaydi.

---

## 🔐 AUTH FLOW

```text
User → login → access + refresh token
→ access token bilan API ishlaydi
→ access expired → refresh token orqali yangilanadi
→ logout → token bekor qilinadi
```

---

# 🔑 1. LOGIN

## POST `/auth/login`

### Purpose

Foydalanuvchini tizimga kiritish va token berish.

---

### Access

Public (authentication talab qilinmaydi)

---

### Request

```json
{
  "login": "string",
  "password": "string"
}
```

---

### Validation

* login mavjud bo‘lishi kerak
* password to‘g‘ri bo‘lishi kerak
* user status = `active` bo‘lishi kerak

---

### Response

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "login": "string",
    "full_name": "string",
    "role": {
      "id": "uuid",
      "name": "admin"
    }
  }
}
```

---

### Errors

| Code | Description                   |
| ---- | ----------------------------- |
| 400  | Invalid request               |
| 401  | Login yoki password noto‘g‘ri |
| 403  | User bloklangan yoki inactive |

---

### DB Tables

* users
* roles
* user_statuses
* audit_logs

---

### Notes

* password hash bilan tekshiriladi (bcrypt)
* login attemptlar log qilinadi
* successful login → `last_login_at` yangilanadi
* audit yoziladi (LOGIN_SUCCESS / LOGIN_FAILED)

---

# 🔄 2. REFRESH TOKEN

## POST `/auth/refresh`

### Purpose

Access token eskirganda yangisini olish.

---

### Access

Public (refresh token talab qilinadi)

---

### Request

```json
{
  "refresh_token": "string"
}
```

---

### Validation

* refresh token valid bo‘lishi kerak
* blacklist’da bo‘lmasligi kerak
* muddati tugamagan bo‘lishi kerak

---

### Response

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Errors

| Code | Description                |
| ---- | -------------------------- |
| 401  | Invalid token              |
| 403  | Token expired yoki revoked |

---

### DB Tables

* audit_logs

---

### Notes

* refresh rotation ishlatiladi (har safar yangi refresh beriladi)
* eski refresh token bekor qilinadi

---

# 🚪 3. LOGOUT

## POST `/auth/logout`

### Purpose

User sessiyasini yopish (tokenlarni bekor qilish).

---

### Access

Authenticated user

---

### Headers

```text
Authorization: Bearer <access_token>
```

---

### Request

```json
{
  "refresh_token": "string"
}
```

---

### Response

```json
{
  "message": "Successfully logged out"
}
```

---

### DB Tables

* audit_logs

---

### Notes

* refresh token blacklist’ga qo‘shiladi
* optional: access token ham blacklist qilinadi
* audit yoziladi (LOGOUT)

---

# 👤 4. CURRENT USER

## GET `/auth/me`

### Purpose

Joriy login qilgan user ma’lumotlarini olish.

---

### Access

Authenticated user

---

### Headers

```text
Authorization: Bearer <access_token>
```

---

### Response

```json
{
  "id": "uuid",
  "login": "string",
  "first_name": "string",
  "last_name": "string",
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "role": {
    "id": "uuid",
    "name": "admin"
  },
  "status": "active",
  "assigned_region_id": "uuid",
  "assigned_service_id": "uuid"
}
```

---

### DB Tables

* users
* roles

---

### Notes

* frontend user context uchun ishlatiladi
* har requestda qayta chaqirilishi mumkin

---

# 🔐 5. CHANGE PASSWORD

## POST `/auth/change-password`

### Purpose

User o‘z parolini o‘zgartiradi.

---

### Access

Authenticated user

---

### Request

```json
{
  "current_password": "string",
  "new_password": "string"
}
```

---

### Validation

* current_password to‘g‘ri bo‘lishi kerak
* new_password minimum security talablariga javob berishi kerak

---

### Response

```json
{
  "message": "Password updated successfully"
}
```

---

### DB Tables

* users
* audit_logs

---

### Notes

* password hash qilinadi
* audit yoziladi (PASSWORD_CHANGED)

---

# 🔒 SECURITY RULES

* JWT ishlatiladi (Bearer token)
* passwordlar faqat hash holatda saqlanadi
* refresh token rotation ishlatiladi
* token blacklist qo‘llab-quvvatlanadi
* har login/logout audit qilinadi

---

# 📌 SUMMARY

Auth moduli:

* xavfsiz login ta’minlaydi
* token orqali autentifikatsiya qiladi
* sessiyani boshqaradi
* barcha kirish harakatlarini audit qiladi

Bu modul butun tizimning **xavfsizlik asosi** hisoblanadi.
