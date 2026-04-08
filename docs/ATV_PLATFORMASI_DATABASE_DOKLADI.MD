# ATV PLATFORMASI DATABASE DOKLADI (YANGILANGAN)
- [database.sql](../database.sql)
- [drawDB](https://drawdb.vercel.app/editor?shareId=59b2556000df75fced032f31d52b5ed6)

## 1. Maqsad
Ushbu schema ATV platformasida quyidagi yo'nalishlarni qamrab oladi:
- texnikalar (assetlar) reyestri,
- hudud/xizmat bo'yicha taqsimot,
- sklad va ehtiyot qismlar harakati,
- ta'mirlash jarayoni va xarajatlar,
- hujjatlashtirish va ruxsat (request) oqimi,
- vazifalar, xabarnomalar, audit va analitika snapshotlari.

## 2. Modellar kategoriyalari (to'liq)
Quyida `database.sql` dagi **40 ta model** toifalar bo'yicha ajratildi.

### A) Xavfsizlik va ruxsatlar (RBAC)
- `roles`
- `permissions`
- `role_permissions`
- `user_statuses`

### B) Hudud va xizmat strukturalari
- `regions`
- `services`
- `region_services`

### C) Foydalanuvchilar
- `users`

### D) Texnika katalogi va klassifikatsiya
- `asset_categories`
- `manufacturers`
- `asset_models`
- `documents`

### E) Lookup/status jadvallar
- `asset_statuses`
- `lifecycle_stages`
- `repair_statuses`
- `expense_types`
- `task_statuses`

### F) Sklad va qismlar (inventory)
- `warehouses`
- `warehouse_documents`
- `parts`
- `warehouse_part_stock`
- `warehouse_part_movements`

### G) Asosiy asset boshqaruvi
- `assets`
- `asset_state_history`
- `asset_transfers`
- `asset_parts`
- `asset_assignments`

### H) Ta'mirlash va xarajatlar
- `repairs`
- `repair_parts`
- `repair_status_history`
- `expenses`

### I) Operatsion modul (tasks/notifications)
- `tasks`
- `notifications`
- `notification_recipients`

### J) Audit va biriktirmalar
- `audit_logs`
- `attachments`

### K) Analitika
- `analytics_snapshots`

### L) Request/commission oqimi
- `requests`
- `request_items`
- `asset_commissions`

## 3. Har bir model bo'yicha qisqa izoh

### RBAC
- `roles`: tizim rollari.
- `permissions`: granular huquqlar (`assets.read`, `analytics.view` va h.k.).
- `role_permissions`: role-permission M:N bog'lanishi.
- `user_statuses`: user holatlari lug'ati.

### Hudud/xizmat
- `regions`: hudud daraxti (`parent_id`).
- `services`: xizmat yo'nalishlari.
- `region_services`: region va service M:N bog'lanishi.

### User
- `users`: autentifikatsiya va operatsion profil (role/status/region/service, 2FA, login statistikasi).

### Texnika katalogi
- `asset_categories`: texnika kategoriyalari (ierarxik).
- `manufacturers`: ishlab chiqaruvchilar.
- `asset_models`: model + manufacturer + category + life/warranty.
- `documents`: rasmiy hujjatlar (transfer/commission/repair/write-off aktlar).

### Lookup
- `asset_statuses`: asset holat kodlari.
- `lifecycle_stages`: hayot sikli bosqichlari.
- `repair_statuses`: ta'mir jarayoni statuslari.
- `expense_types`: xarajat turlari.
- `task_statuses`: task holatlari.

### Sklad
- `warehouses`: omborlar.
- `warehouse_documents`: omborga oid kirim/chiqim hujjat bog'lanmalari.
- `parts`: ehtiyot qismlar katalogi.
- `warehouse_part_stock`: ombor kesimida qoldiq.
- `warehouse_part_movements`: kirim/chiqim tarix harakati.

### Asset yadrosi
- `assets`: asosiy texnika reyestri.
- `asset_state_history`: asset holati tarixi.
- `asset_transfers`: region/service/warehouse ko'chirish tarixi.
- `asset_parts`: asset tarkibidagi qismlar.
- `asset_assignments`: assetni region/service ga biriktirish tarixi.

### Ta'mir/xarajat
- `repairs`: ta'mir kartochkasi.
- `repair_parts`: ta'mirda ishlatilgan qismlar.
- `repair_status_history`: ta'mir status evolyutsiyasi.
- `expenses`: operatsion xarajatlar.

### Operatsion
- `tasks`: ichki vazifalar.
- `notifications`: tizim xabarlari.
- `notification_recipients`: xabarni olgan/o'qigan foydalanuvchilar.

### Audit va fayl
- `audit_logs`: o'zgarishlar izi (actor/entity/action/old/new).
- `attachments`: universal fayl biriktirish.

### Analitika
- `analytics_snapshots`: davriy KPI agregatlari.

### Request/Commission
- `requests`: ruxsat so'rovlari.
- `request_items`: request tarkibi (model + quantity).
- `asset_commissions`: assetni hujjat asosida commission qilish yozuvi.

## 4. Asosiy bog'lanishlar (yuqori daraja)
- RBAC: `users -> roles -> role_permissions -> permissions`
- Klassifikatsiya: `assets -> asset_models -> (manufacturers, asset_categories)`
- Joylashuv/xizmat: `assets -> (regions, services, warehouses)`
- Sklad: `warehouse_part_stock` va `warehouse_part_movements` orqali `parts` qoldig'i
- Ta'mir: `repairs -> repair_parts -> parts`, status audit `repair_status_history`
- Xarajat: `expenses` asset/repair/region/service/type bilan bog'lanadi
- Xabar: `notifications -> notification_recipients -> users`
- Request oqimi: `requests -> request_items`, keyin `asset_commissions` va `documents`

## 5. Eslatma (oldingi versiyadan farqlar)
Ushbu yangilangan hujjat faqat amaldagi `database.sql` ga asoslangan.
Quyidagi modellar **amaldagi sxemada yo'q** va hujjatdan chiqarildi:
- `user_scopes`
- `forecasts`
- `calendar_events`

## 6. Yakuniy natija
Hozirgi holatda barcha modellar:
- to'liq ajratilgan,
- kategoriyalar bo'yicha tarqatilgan,
- amaldagi schema bilan mos holatga keltirilgan.
