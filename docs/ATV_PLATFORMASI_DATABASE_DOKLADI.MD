# ATV PLATFORMASI DATABASE DOKLADI
[database.sql](/database.sql)
## 1. Platformaning asosiy vazifasi

Bu baza ATV platformasi uchun yaratilgan va uning vazifasi:

* texnik vositalarni yagona reyestrda saqlash,
* hudud va xizmat kesimida taqsimotni ko‘rsatish,
* sklad va qismlar harakatini nazorat qilish,
* texnika hayot sikli va ta’mir tarixini saqlash,
* xarajatlar va prognozlarni tahlil qilish,
* audit va xavfsizlikni ta’minlash.

Bu tizim oddiy CRUD emas. Bu boshqaruv, nazorat, analiz va prognoz platformasi. Shu sababli ma’lumotlar bir-biridan ajratilgan, lekin o‘zaro bog‘langan holda saqlanadi.

---

# 2. Database arxitekturasi qanday ishlaydi

Schema 6 ta katta blokdan tashkil topgan:

1. **Xavfsizlik va ruxsatlar**
2. **Hududiy tuzilma va xizmatlar**
3. **Foydalanuvchilar**
4. **Texnika katalogi**
5. **Sklad, qismlar, ta’mir va tarix**
6. **Audit, xabarnoma, tasks, forecast**

Shu bo‘linish backend yozishni juda oson qiladi, chunki har bir service o‘z mas’uliyatiga ega bo‘ladi: auth service, asset service, warehouse service, repair service, analytics service, audit service.

---

# 3. Har bir jadval nima uchun kerak

## A. Xavfsizlik va huquqlar

### `roles`

Foydalanuvchi rollari saqlanadi: masalan `superadmin`, `admin`, `moderator`, `analyst`. Bu jadval access control’ning asosidir. Har bir user faqat bitta role’ga bog‘lanadi.

### `permissions`

Rolga berilishi mumkin bo‘lgan aniq huquqlar saqlanadi: masalan `assets.read`, `analytics.view`, `repairs.edit`. Bu juda muhim, chunki katta tizimda “admin” va “analyst” bir xil huquqqa ega bo‘lmasligi kerak.

### `role_permissions`

Bu ko‘pdan-ko‘pga bog‘lanish jadvali. Bitta rol ko‘p permission olishi mumkin, bir permission esa bir nechta rolda ishlatilishi mumkin. Bu RBAC’ni to‘g‘ri qurish uchun kerak.

### `user_statuses`

User holatlari uchun lookup jadval: faol, bloklangan, arxivlangan va hokazo. Bu statusni kod bilan boshqarish backendda logika yozishni osonlashtiradi.

### `user_scopes`

User ko‘ra oladigan hudud yoki xizmat doirasini saqlaydi. Bu ayniqsa admin va analyst uchun foydali: ular butun tizimni emas, faqat ruxsat etilgan scope’ni ko‘radi.

---

## B. Hududiy tuzilma va xizmatlar

### `regions`

Tashkilotning hududiy ierarxiyasi saqlanadi: respublika → viloyat → tuman → bo‘linma. `parent_id` orqali daraxt ko‘rinishida ishlaydi. Bu texnikani hudud bo‘yicha tahlil qilish uchun bazaviy jadval.

### `services`

Xizmat yo‘nalishlari saqlanadi: masalan, yo‘l patruli, tergov, aloqa va IT, maxsus bo‘linmalar. Bu jadval texnikani xizmat kesimida ko‘rsatadi.

### `region_services`

Qaysi hududda qaysi xizmat mavjudligini bog‘lovchi jadval. Bu ham ko‘pdan-ko‘pga relationship. Hudud va xizmatni bir-biridan mustaqil saqlab, keyin bog‘lash uchun ishlatiladi.

---

## C. Foydalanuvchilar

### `users`

Tizim foydalanuvchilari shu yerda saqlanadi. Login, parol xeshi, ism, familiya, email, telefon, role, status, tayinlangan hudud va xizmat, oxirgi kirish, 2FA, failed attempts, version kabi maydonlar bor. Backend login, permission check, session control va audit uchun aynan shu jadvalga tayangan bo‘ladi.

---

## D. Texnika tasnifi

### `asset_categories`

Texnika kategoriyalari saqlanadi: kompyuter, server, kamera, printer va boshqalar. `parent_id` orqali kategoriyalarni ierarxik qilsa bo‘ladi. Bu analiz va filtrlar uchun juda foydali.

### `manufacturers`

Ishlab chiqaruvchilar ro‘yxati. Masalan Dell, HP, Lenovo, Huawei va hokazo. Model va detal bu jadvalga bog‘lanadi.

### `asset_models`

Texnikaning modeli saqlanadi. Har bir model ishlab chiqaruvchi va kategoriya bilan bog‘langan. Bu juda muhim, chunki asset’ni “nimadan iborat” degan savolga shu jadval javob beradi. Shuningdek, lifetime va warranty shu yerda turadi.

---

## E. Status va lookup jadvallar

### `asset_statuses`

Asset’ning joriy holati: faol, zahirada, nosoz, hisobdan chiqarilgan. Bu statuslar kod bilan boshqariladi, shuning uchun backendda hardcode kamayadi.

### `lifecycle_stages`

Texnika hayot sikli bosqichlari: new, normal, old, critical. Bu eskirishni hisoblash va prognoz qilishda kerak.

### `repair_statuses`

Ta’mir statuslari: reported, in_progress, done, canceled. Repair workflow shu jadvalga tayangan bo‘ladi.

### `expense_types`

Xarajat turlari: repair, maintenance, purchase, adjustment kabi tasniflar shu yerda yuritiladi. Bu tahlil va byudjet hisobi uchun kerak.

### `task_statuses`

Task’lar holati: open, in_progress, done, canceled. Bu operatsion ishlarni boshqarish uchun kerak.

---

## F. Sklad va qismlar

### `warehouses`

Skladlar saqlanadi. Har bir warehouse qaysi regionga tegishli ekani va mas’ul user kimligi ko‘rsatiladi. Bu texnika yoki qismlar qayerda saqlanayotganini boshqarish uchun kerak.

### `parts`

Qismlar katalogi. Masalan RAM, SSD, motherboard, sensor va hokazo. Bu alohida saqlanadi, chunki qismlar texnika bilan bir xil emas.

### `warehouse_part_stock`

Har bir skladdagi har bir qismning joriy qoldig‘ini saqlaydi. Bu “hozir omborda nechta bor?” degan savolga tez javob beradi. `warehouse_id + part_id` composite PK bilan ishlaydi.

### `warehouse_part_movements`

Skladga kirim va chiqim harakatlari saqlanadi. `IN` va `OUT` orqali qism harakati izlanadi. Bu inventory audit va qoldiq hisoblash uchun juda muhim.

---

## G. Asosiy texnik vosita

### `assets`

Bu platformaning eng muhim jadvali. Har bir real texnika shu yerda hisobga olinadi. Unda asset tag, serial number, model, service, region, warehouse, purchase date, commission date, warranty, purchase cost, status, lifecycle, condition, responsible user, metadata, soft delete va version mavjud.

Bu jadval backend’da asosiy obyekt bo‘ladi. Devor ichida qolgan barcha servislar shu jadval atrofida ishlaydi.

### `asset_state_history`

Asset holatining o‘zgarish tarixi saqlanadi. Bu analitika, audit va AI prognoz uchun juda kerak. Masalan, texnika qachon nosoz bo‘lgan, qachon repair’ga ketgan, qachon condition pasaygan — hammasi shu yerda.

### `asset_transfers`

Asset qayerdan qayerga ko‘chganini saqlaydi. Region, service va warehouse o‘zgarishlari shu jadvalda tarix sifatida qoladi. Bu ko‘chirishni bloklash va real tracking uchun kerak.

---

## H. Asset va parts bog‘lanishi

### `asset_parts`

Bu jadval asset ichida qaysi qismlar ishlatilganini ko‘rsatadi. Masalan, bitta kompyuter uchun qaysi CPU, RAM, SSD ishlatilgan. Bu assembly logikasi uchun kerak.

---

## I. Ta’mirlash

### `repairs`

Ta’mir yozuvlari shu yerda saqlanadi. Qaysi asset uchun ta’mir ochilgan, kim report qilgan, kimga biriktirilgan, kim bajargan, statusi, ta’mir sanasi, tavsifi va umumiy xarajati shu yerda yuritiladi.

### `repair_parts`

Ta’mir paytida ishlatilgan qismlar shu jadvalda saqlanadi. Bu repair cost va spare part consumption’ni hisoblashga yordam beradi.

### `repair_status_history`

Ta’mir statusining o‘zgarish tarixi. Masalan, reported → in_progress → done. Bu workflow nazorati uchun kerak.

---

## J. Xarajatlar va prognoz

### `expenses`

Asset, repair, region, service va expense type bilan bog‘langan xarajatlar shu jadvalda saqlanadi. Bu byudjetni tahlil qilish uchun markaziy manba.

### `forecasts`

Kelajak ehtiyoj prognozlari saqlanadi. Qaysi region, service va category uchun qaysi yilga qancha ehtiyoj bo‘lishi taxmin qilinganini ko‘rsatadi. Bu rahbariyatga reja tuzishda yordam beradi.

---

## K. Operatsion yordamchi jadvallar

### `tasks`

Ichki topshiriqlar jadvali. Asset bilan bog‘liq bajarilishi kerak bo‘lgan ishlar, muddat, assigned user va status shu yerda yuritiladi.

### `notifications`

Tizim ichidagi xabarlar uchun. Masalan, yangi repair, yangi transfer, yangi task yoki audit hodisasi bo‘yicha xabar.

### `notification_recipients`

Qaysi user qaysi xabarni olganini va o‘qigan-o‘qimaganini saqlaydi. Bitta notification ko‘p userga yuborilishi mumkin.

### `attachments`

Fayllar biriktirish uchun universal jadval. Hujjatlar, suratlar, aktlar, skanlar shu yerda saqlanadi. Entity type va entity id orqali har qanday obyektga bog‘lanadi.

### `calendar_events`

Rejalashtirilgan uchrashuvlar, tekshiruvlar yoki tadbirlar shu jadvalda. Backend’da ops/planning moduliga kerak bo‘ladi.

---

## L. Audit

### `audit_logs`

Tizimdagi eng muhim xavfsizlik jadvalaridan biri. Kim nima qildi, qachon qildi, qaysi obyektga tegishli edi, oldingi va yangi qiymatlar qanday edi — hammasi shu yerda. Anonymous foydalanuvchini ham loglash mumkin.

Bu jadval:

* security,
* compliance,
* investigation,
* debugging

uchun kerak.

---

# 4. Jadvallar bir-biri bilan qanday ulanadi

Quyidagi asosiy oqim mavjud:

### 1. User tizimga kiradi

`users` → `roles` → `role_permissions` → `permissions`
Bu user qaysi amallarni qila olishini belgilaydi.

### 2. User qaysi joyni ko‘rishini belgilaydi

`users` → `assigned_region_id`, `assigned_service_id`
Qo‘shimcha scope kerak bo‘lsa `user_scopes`.

### 3. Asset yaratiladi

`assets` → `asset_models` → `manufacturers` → `asset_categories`
Bu texnika nimaligini aniq ko‘rsatadi.

### 4. Asset joylashadi

`assets` → `regions` yoki `warehouses`
Bu asset ombordami yoki ishlatilayotgan hududdami degan savolga javob beradi.

### 5. Asset buzilsa

`repairs` → `repair_parts` → `parts`
Ta’mir statusi `repair_status_history` orqali ko‘rinadi.

### 6. Qism ombordan chiqsa

`warehouse_part_movements` → `warehouse_part_stock`
Bu real inventory nazoratini beradi.

### 7. Har bir o‘zgarish yozib boriladi

`audit_logs`
Bu tizimni xavfsiz qiladi.

---

# 5. Backend yozishda bu schema qanday yordam beradi

Bu model backend uchun juda qulay, chunki u aniq domenlarga bo‘lingan. Natijada:

* `AuthService` → `users`, `roles`, `permissions`
* `OrgService` → `regions`, `services`, `region_services`
* `AssetService` → `assets`, `asset_state_history`, `asset_transfers`
* `WarehouseService` → `warehouses`, `parts`, `warehouse_part_stock`, `warehouse_part_movements`
* `RepairService` → `repairs`, `repair_parts`, `repair_status_history`
* `FinanceService` → `expenses`, `forecasts`
* `AuditService` → `audit_logs`
* `NotificationService` → `notifications`, `notification_recipients`

Bu bo‘linish backendni:

* test qilishni,
* kodni saqlashni,
* scaling qilishni,
* permissions’ni boshqarishni,
* service layer yozishni

ancha osonlashtiradi.

---

# 6. Qisqa texnik tavsiya

Agar men bu loyihani yozayotgan bo‘lsam, backend’da quyidagicha bo‘laman:

* `domain` bo‘yicha modul qilish
* `repository` layer alohida
* `service` layer alohida
* `api/router` alohida
* `audit` middleware alohida
* `RBAC` dependency alohida
* `history` yozishni service ichida qilish
* warehouse update’larni transaction bilan bajarish

---

# 7. Rahbariyatga aytish uchun qisqa xulosa

Bu platforma:

* texnikani hisobga oladi,
* skladni boshqaradi,
* ta’mirni nazorat qiladi,
* xarajatni ko‘rsatadi,
* kelajak ehtiyojni taxmin qiladi,
* barcha harakatlarni loglaydi.

Ya’ni bu tizimning maqsadi faqat “ma’lumot saqlash” emas. Maqsad — **qaror qabul qilishni faktga asoslash**.

---

# 8. Sen uchun eng muhim mapping

Agar backend yozayotganda bu schema’ni boshda ushlash qiyin bo‘lsa, shuni yodla:

* **User** → kim ishlaydi
* **Region / Service** → qayerda ishlaydi
* **Asset** → nima bor
* **Warehouse / Part** → zaxira nima
* **Repair** → nima buzildi
* **Expense** → qancha ketdi
* **Forecast** → keyin nima kerak bo‘ladi
* **Audit** → kim nima qildi
