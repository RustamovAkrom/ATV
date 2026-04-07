CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ATV platform uchun optimallashtirilgan relational schema
-- Maqsad: texnika reyestri, sklad, assembly/parts, tarix, audit va RBAC

-- =========================================================
-- 1) Xavfsizlik va huquqlar
-- =========================================================
-- Rollar jadvali - bu jadvalga tizimdagi rollar (masalan, superadmin, admin, moderator, analyst va hokazo) haqida ma'lumot saqlanadi. Har bir rol o'ziga xos nomga ega bo'ladi va bu nom rolning qaysi turga tegishli ekanligini ko'rsatadi. Bu jadval orqali rollarni boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS roles (
    id UUID,
    name VARCHAR(100) NOT NULL UNIQUE,         -- Rol nomi: superadmin, admin, moderator, analyst
    description TEXT,                          -- Rol izohi
    PRIMARY KEY (id)
);

-- Permissionlar jadvali - bu jadvalga tizimdagi barcha mumkin bo'lgan huquqlar (permissions) saqlanadi. Har bir permission o'ziga xos kodga ega bo'ladi va bu kod tizimdagi aniq bir harakat yoki resursga ruxsat berishni ifodalaydi. Masalan, permission kodi "assets.read" bo'lsa, bu rolga ega foydalanuvchilar texnika reyestrini o'qish huquqiga ega bo'lishadi. Bu jadval orqali rollarga kerakli huquqlarni tayinlash va boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS permissions (
    id UUID,
    code VARCHAR(150) NOT NULL UNIQUE,         -- Permission kodi: assets.read, analytics.view va hokazo
    name VARCHAR(255),                         -- Odam o'qiydigan nom
    description TEXT,                          -- Batafsil izoh
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Qaysi rolga qaysi permission berilganligini ko'rsatadi. Bu jadval orqali rollarga kerakli huquqlarni tayinlash va boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID NOT NULL,                     -- Qaysi rolga beriladi
    permission_id UUID NOT NULL,               -- Qaysi permission beriladi
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id)
);

-- Foydalanuvchi statuslari - bu jadvalga tizimdagi foydalanuvchilarning hozirgi holatini ko'rsatadigan statuslar saqlanadi. Har bir status o'ziga xos kodga ega bo'ladi va bu kod foydalanuvchining hozirgi holatini aniqlash uchun ishlatiladi. Masalan, foydalanuvchi statuslari "active" (faol), "blocked" (bloklangan) yoki "archived" (arxivlangan) bo'lishi mumkin. Bu jadval orqali foydalanuvchilarning holatini boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS user_statuses (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- Faol / bloklangan / arxivlangan
    description TEXT,
    PRIMARY KEY (code)
);

-- =========================================================
-- 2) Hududiy tuzilma va xizmatlar
-- =========================================================
-- Hududlar jadvali - bu jadvalga tizimdagi hududlar (masalan, respublika, viloyat, tuman, bo'linma va hokazo) haqida ma'lumot saqlanadi. Har bir hudud o'ziga xos nomga ega bo'ladi va bu nom hududning qaysi turga tegishli ekanligini ko'rsatadi. Bu jadval orqali hududlarni boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS regions (
    id UUID,
    name VARCHAR(255) NOT NULL,                -- Hudud nomi
    code VARCHAR(50) UNIQUE,                   -- Qisqa kod
    level SMALLINT,                            -- 1-respublika, 2-viloyat, 3-tuman, 4-bo'linma
    parent_id UUID,                            -- Yuqori hudud
    latitude DOUBLE PRECISION,                 -- Markaz koordinatalari
    longitude DOUBLE PRECISION,                -- Markaz koordinatalari
    geojson JSONB,                             -- Aniq hudud shakli uchun
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Xizmatlar jadvali - bu jadvalga tizimdagi xizmatlar (masalan, IT, transport, kommunal va hokazo) haqida ma'lumot saqlanadi. Har bir xizmat o'ziga xos nomga ega bo'ladi va bu nom xizmatning qaysi turga tegishli ekanligini ko'rsatadi. Bu jadval orqali xizmatlarni boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS services (
    id UUID,
    name VARCHAR(255) NOT NULL UNIQUE,         -- Xizmat nomi
    code VARCHAR(50) UNIQUE,                   -- Xizmat kodi
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Qaysi hududda qaysi xizmatlar mavjudligini ko'rsatadi. Bu jadval orqali foydalanuvchilarga hudud va xizmatlarga asoslangan ruxsatlarni boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS region_services (
    region_id UUID NOT NULL,                   -- Hudud
    service_id UUID NOT NULL,                  -- Xizmat
    PRIMARY KEY (region_id, service_id)
);

-- Foydalanuvchining qo'shimcha ko'rish doirasi.
-- Bu jadval admin/analyst uchun bir nechta hudud yoki xizmatga ruxsat berishda foydali.
CREATE TABLE IF NOT EXISTS user_scopes (
    id UUID,
    user_id UUID NOT NULL,
    region_id UUID,
    service_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id),
    UNIQUE (user_id, region_id, service_id)
);

-- =========================================================
-- 3) Foydalanuvchilar
-- =========================================================
-- Bu jadvalga tizim foydalanuvchilari haqida batafsil ma'lumot saqlanadi. Har bir foydalanuvchi o'ziga xos identifikator, login, parol, ismi, familiyasi, emaili, telefoni, roli, statusi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali foydalanuvchilarni boshqarish, ularning huquqlarini belgilash va tizimga kirishlarini nazorat qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS users (
    id UUID,
    login VARCHAR(100) NOT NULL UNIQUE,        -- Tizimga kirish logini
    password_hash VARCHAR(255) NOT NULL,       -- Xeshlangan parol
    first_name VARCHAR(100),                    -- Ism
    last_name VARCHAR(100),                     -- Familiya
    email VARCHAR(255) UNIQUE,                  -- Email
    phone VARCHAR(20) UNIQUE,                  -- Telefon
    role_id UUID NOT NULL,                     -- Rolga bog'lanadi
    status_code VARCHAR(50),                   -- Foydalanuvchi statusi
    assigned_region_id UUID,                   -- Asosiy hudud
    assigned_service_id UUID,                  -- Asosiy xizmat
    last_login TIMESTAMP WITH TIME ZONE,       -- Oxirgi kirish vaqti
    last_password_change TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    is_two_factor_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,                 -- Optimistic locking uchun
    PRIMARY KEY (id)
);

-- =========================================================
-- 4) Texnika tasnifi
-- =========================================================
-- Asset kategoriyalari - bu jadvalga tizimdagi texnikalarning kategoriyalari saqlanadi. Har bir kategoriya o'ziga xos nomga ega bo'ladi va bu nom texnikaning qaysi turga tegishli ekanligini ko'rsatadi. Masalan, asset kategoriyalari "kompyuter", "server", "kamera" yoki "printer" bo'lishi mumkin. Bu jadval orqali texnikalarni kategoriyalarga ajratish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_categories (
    id UUID,
    name VARCHAR(150) NOT NULL,                -- Kategoriya nomi: kompyuter, server, kamera va hokazo
    code VARCHAR(50) UNIQUE,                   -- Ichki kod
    parent_id UUID,                            -- Kategoriya ierarxiyasi
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Ishlab chiqaruvchilar jadvali - bu jadvalga har bir ishlab chiqaruvchi haqida batafsil ma'lumot saqlanadi. Har bir ishlab chiqaruvchi o'ziga xos identifikator, nomi, mamlakati, veb-sayti va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali ishlab chiqaruvchilarni boshqarish, ularning mahsulotlarini tahlil qilish va ta'minot zanjirini optimallashtirish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS manufacturers (
    id UUID,
    name VARCHAR(150) NOT NULL UNIQUE,         -- Ishlab chiqaruvchi nomi
    country VARCHAR(100),                      -- Mamlakat
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Har bir model qaysi kategoriyaga va ishlab chiqaruvchiga tegishli ekanligini ko'rsatadi. Shuningdek, normativ xizmat muddati va kafolat muddati kabi atributlar ham mavjud bo'ladi. Bu jadval orqali assetlarni standartlashtirish, tahlil qilish va prognoz qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_models (
    id UUID,
    name VARCHAR(150) NOT NULL,                -- Model nomi
    manufacturer_id UUID NOT NULL,             -- Ishlab chiqaruvchi
    category_id UUID NOT NULL,                 -- Kategoriya
    lifetime_years INTEGER,                    -- Normativ xizmat muddati
    warranty_months INTEGER,                   -- Kafolat muddati
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id),
    UNIQUE (name, manufacturer_id)
);

-- =========================================================
-- 5) Statuslar va lookup jadvallar
-- =========================================================
-- Asset statuslari - bu jadvalga tizimdagi texnikalarning hozirgi holatini ko'rsatadigan statuslar saqlanadi. Har bir status o'ziga xos kodga ega bo'ladi va bu kod texnikaning hozirgi holatini aniqlash uchun ishlatiladi. Masalan, asset statuslari "active" (faol), "in_stock" (zahirada), "broken" (nosoz) yoki "retired" (hisobdan chiqarilgan) bo'lishi mumkin. Bu jadval orqali texnikalarning holatini boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_statuses (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- Faol / zahirada / nosoz / hisobdan chiqarilgan
    description TEXT,
    PRIMARY KEY (code)
);

-- Hayot sikli bosqichlari - bu jadvalga tizimdagi texnikalarning hayot siklining qaysi bosqichida ekanligini ko'rsatadigan kodlar saqlanadi. Har bir bosqich o'ziga xos kodga ega bo'ladi va bu kod texnikaning hozirgi holatini aniqlash uchun ishlatiladi. Masalan, hayot sikli bosqichlari "new" (yangi), "normal" (normal), "old" (eski) yoki "critical" (tanqidiy) bo'lishi mumkin. Bu jadval orqali texnikalarning hayot siklini boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS lifecycle_stages (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- NEW / NORMAL / OLD / CRITICAL
    description TEXT,
    PRIMARY KEY (code)
);

-- Ta'mir statuslari - bu jadvalga tizimdagi ta'mirlarning hozirgi holatini ko'rsatadigan statuslar saqlanadi. Har bir status o'ziga xos kodga ega bo'ladi va bu kod ta'mirning hozirgi holatini aniqlash uchun ishlatiladi. Masalan, ta'mir "reported" (xabar qilingan), "in_progress" (jarayonda), "done" (bajarilgan) yoki "canceled" (bekor qilingan) bo'lishi mumkin. Bu jadval orqali ta'mirlarning holatini boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS repair_statuses (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- reported / in_progress / done / canceled
    description TEXT,
    sort_order INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    PRIMARY KEY (code)
);

-- Xarajat turlari - bu jadvalga tizimdagi xarajatlarning turlarini ko'rsatadigan kodlar saqlanadi. Har bir xarajat turi o'ziga xos kodga ega bo'ladi va bu kod xarajatning qaysi turga tegishli ekanligini aniqlash uchun ishlatiladi. Masalan, xarajat turi "repair" (ta'mir), "replacement" (almashish), "consumables" (sarflanadigan materiallar) yoki "other" (boshqa) bo'lishi mumkin. Bu jadval orqali xarajatlarni tahlil qilish, kategoriyalarga ajratish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS expense_types (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- Xarajat turi
    description TEXT,
    PRIMARY KEY (code)
);

-- Task statuslari - bu jadvalga tizimdagi vazifalarning hozirgi holatini ko'rsatadigan statuslar saqlanadi. Har bir status o'ziga xos kodga ega bo'ladi va bu kod vazifaning hozirgi holatini aniqlash uchun ishlatiladi. Masalan, vazifa "open" (ochiq), "in_progress" (jarayonda), "done" (bajarilgan) yoki "canceled" (bekor qilingan) bo'lishi mumkin. Bu jadval orqali vazifalarning holatini boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS task_statuses (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- open / in_progress / done / canceled
    description TEXT,
    sort_order INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    PRIMARY KEY (code)
);

-- =========================================================
-- 6) Sklad (warehouse) va parts
-- =========================================================
-- Ombor jadvali - bu jadvalga har bir ombor haqida batafsil ma'lumot saqlanadi. Har bir ombor o'ziga xos identifikator, kodi, nomi, joylashuvi, mas'ul xodimi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali omborlarni boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS warehouses (
    id UUID,
    code VARCHAR(50) UNIQUE,                   -- Ombor kodi
    name VARCHAR(255) NOT NULL,                -- Ombor nomi
    region_id UUID,                            -- Qaysi hududdagi ombor
    manager_user_id UUID,                      -- Mas'ul xodim
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Qismlar jadvali - bu jadvalga har bir qism (part) haqida batafsil ma'lumot saqlanadi. Har bir qism o'ziga xos identifikator, nomi, ishlab chiqaruvchisi, o'lchov birligi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali qismlarni boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS parts (
    id UUID,
    part_number VARCHAR(100) UNIQUE,           -- Qism kodi/part number
    name VARCHAR(255) NOT NULL,                -- Qism nomi
    manufacturer_id UUID,                      -- Qism ishlab chiqaruvchisi
    unit VARCHAR(30) DEFAULT 'pcs',            -- O'lchov birligi
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Ombordagi qismlar qoldig'i.
-- Bu jadval parts uchun current stock holatini tez olishga yordam beradi.
CREATE TABLE IF NOT EXISTS warehouse_part_stock (
    warehouse_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0, -- Hozirgi qoldiq
    min_quantity INTEGER DEFAULT 0,              -- Minimal tavsiya etilgan qoldiq
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (warehouse_id, part_id)
);

-- Omborga kirim/chiqim harakati:
-- movement_type = IN yoki OUT
CREATE TABLE IF NOT EXISTS warehouse_part_movements (
    id UUID,
    warehouse_id UUID NOT NULL,
    part_id UUID NOT NULL,
    movement_type VARCHAR(10) NOT NULL,         -- IN / OUT
    quantity INTEGER NOT NULL,                  -- Miqdor
    reference_type VARCHAR(50),                 -- purchase / repair / adjustment / transfer
    reference_id UUID,                          -- Bog'langan obyekt ID
    moved_by UUID,                              -- Kim amalga oshirdi
    moved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    note TEXT,
    PRIMARY KEY (id)
);

-- =========================================================
-- 7) Asosiy assetlar
-- =========================================================
-- Bu jadvalga har bir texnika (asset) haqida batafsil ma'lumot saqlanadi. Har bir asset o'ziga xos identifikator, modeli, joylashuvi, holati, xarid sanasi, kafolat muddati va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali assetlarni boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS assets (
    id UUID,
    asset_tag VARCHAR(255) UNIQUE,              -- Inventar raqami
    serial_number VARCHAR(255) UNIQUE,          -- Seriya raqami
    model_id UUID NOT NULL,                     -- Model
    service_id UUID,                            -- Xizmat
    region_id UUID,                             -- Joriy hudud
    current_warehouse_id UUID,                  -- Agar omborda tursa, qaysi omborda
    purchase_date DATE,                         -- Xarid sanasi
    commission_date DATE,                       -- Ishga tushirilgan sana
    warranty_end DATE,                          -- Kafolat tugash sanasi
    purchase_cost NUMERIC(18,2),                -- Xarid narxi
    status_code VARCHAR(50),                    -- Joriy status
    last_repair_date DATE,                      -- Oxirgi ta'mir sanasi
    failure_count INTEGER DEFAULT 0,            -- Nosozliklar soni
    usage_intensity INTEGER DEFAULT 0,          -- Foydalanish intensivligi (masalan, soat yoki kilometr)
    lifecycle_stage_code VARCHAR(50),           -- Hayot sikli
    condition_percent INTEGER DEFAULT 100,      -- Holat foizi
    responsible_user_id UUID,                   -- Mas'ul xodim
    is_transfer_locked BOOLEAN DEFAULT false,   -- Ko'chirishni bloklash
    metadata JSONB DEFAULT '{}'::jsonb,         -- Qo'shimcha moslashuvchan ma'lumotlar
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    version INTEGER DEFAULT 1,
    PRIMARY KEY (id)
);

-- Asset holati tarixini saqlash.
-- Bu analitika va prognoz uchun juda muhim.
CREATE TABLE IF NOT EXISTS asset_state_history (
    id UUID,
    asset_id UUID NOT NULL,
    status_code VARCHAR(50),
    lifecycle_stage_code VARCHAR(50),
    condition_percent INTEGER,
    note TEXT,
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Assetning harakat tarixi:
-- Ombordan bo'limga, bo'limdan boshqa hududga, xizmatdan omborga va hokazo.
CREATE TABLE IF NOT EXISTS asset_transfers (
    id UUID,
    asset_id UUID NOT NULL,
    from_region_id UUID,
    to_region_id UUID,
    from_service_id UUID,
    to_service_id UUID,
    from_warehouse_id UUID,
    to_warehouse_id UUID,
    transferred_by UUID,
    transferred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    note TEXT,
    PRIMARY KEY (id)
);

-- =========================================================
-- 8) Assembler/komplektatsiya: asset ↔ parts
-- =========================================================
-- Ba'zi texnikalar bir nechta qismlardan iborat bo'lishi mumkin. Masalan, kompyuter - protsessor, RAM, qattiq disk va hokazo.
CREATE TABLE IF NOT EXISTS asset_parts (
    asset_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,        -- Nechta qism ishlatilgan
    note TEXT,
    added_by UUID,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (asset_id, part_id)
);

-- =========================================================
-- 9) Ta'mirlash
-- =========================================================
-- Ta'mirlar jadvali - bu jadvalga har bir ta'mir operatsiyasi haqida batafsil ma'lumot saqlanadi. Har bir ta'mir qaysi texnikaga tegishli ekanligini, ta'mirni kim xabar qilganini, kimga topshirilganini, kim bajarganini, ta'mir holatini, ta'mir sanasini, ta'mir xarajatlarini va boshqa muhim ma'lumotlarni o'z ichiga oladi. Bu jadval orqali ta'mir jarayonini tahlil qilish, samaradorlikni oshirish va xarajatlarni boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS repairs (
    id UUID,
    asset_id UUID NOT NULL,  -- Qaysi texnikaga ta'mir qilinmoqda
    reported_by UUID, -- Ta'mirni kim xabar qilgan
    assigned_to UUID,  -- Ta'mirni kimga topshirilgan
    performed_by UUID, -- Ta'mirni kim bajargan
    status_code VARCHAR(50), -- reported / in_progress / done / canceled
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    repair_date TIMESTAMP WITH TIME ZONE,  -- Ta'mir bajarilgan sana
    description TEXT,
    total_cost NUMERIC(18,2) DEFAULT 0,  -- Ta'mir xarajatlari
    downtime_hours INTEGER DEFAULT 0,  -- Ta'mir davomiyligi (soatlarda)
    repair_type VARCHAR(50), -- preventive / corrective / emergency || Ta'mir turi (preventiv yoki corrective va hokazo)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    PRIMARY KEY (id)
);
-- Ta'mirda ishlatilgan qismlar va ularning xarajatlarini saqlash. Bu ta'mir xarajatlarini tahlil qilish va qaysi qismlar eng ko'p ishlatilayotganini aniqlash uchun muhimdir.
CREATE TABLE IF NOT EXISTS repair_parts (
    id UUID,
    repair_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    cost NUMERIC(18,2) DEFAULT 0,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Ta'mir holati o'zgarish tarixini saqlash. Bu ta'mir jarayonini tahlil qilish va samaradorlikni oshirish uchun muhimdir.
CREATE TABLE IF NOT EXISTS repair_status_history (
    id UUID,
    repair_id UUID NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- =========================================================
-- 10) Xarajatlar va forecast
-- =========================================================
-- Xarajatlar jadvali - bu jadvalga har bir ta'mir, transfer yoki boshqa operatsiyalar bilan bog'liq bo'lgan xarajatlar saqlanadi. Har bir xarajat qaysi assetga, ta'mirga, hududga va xizmatga tegishli ekanligini ko'rsatadi. Bu jadval orqali umumiy xarajatlarni tahlil qilish, eng ko'p xarajat qilinadigan hududlar yoki xizmatlarni aniqlash va kelgusi xarajatlarni prognoz qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS expenses (
    id UUID,
    asset_id UUID,
    repair_id UUID,
    region_id UUID,
    service_id UUID,
    expense_type_code VARCHAR(50),
    amount NUMERIC(18,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'UZS',
    description TEXT,
    created_by UUID,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_url VARCHAR(2048),
    PRIMARY KEY (id)
);

-- Forecast jadvali - bu jadvalga har bir hudud, xizmat va texnika kategoriyasi uchun kelgusi yillardagi ehtiyoj va xarajatlar bo'yicha prognozlar saqlanadi. Bu jadval analitik va rejalashtirish uchun juda muhimdir.
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID,
    region_id UUID,
    service_id UUID,
    asset_category_id UUID,
    forecast_year INTEGER NOT NULL,
    demand_estimate INTEGER NOT NULL,           -- Taxmin qilingan ehtiyoj soni
    method VARCHAR(100),                        -- Statistik yoki AI usuli
    confidence NUMERIC(5,2),                    -- Ishonchlilik foizi
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- =========================================================
-- 11) Task / Notification / Audit / Attachment
-- =========================================================
-- Tasks jadvali - bu jadvalga texnika bilan bog'liq bo'lgan yoki bo'lmagan, lekin tizim ichidagi muhim vazifalar (masalan, ta'mir qilish, tekshirish, yangilash va hokazo) saqlanadi. Har bir vazifa qaysi assetga tegishli ekanligini va uning hozirgi holatini ko'rsatadi.
CREATE TABLE IF NOT EXISTS tasks (
    id UUID,
    asset_id UUID,
    title VARCHAR(250) NOT NULL,                -- Vazifa sarlavhasi
    description TEXT,
    status_code VARCHAR(50),
    assigned_to UUID,
    due_date TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Notifications jadvali - bu jadval tizimdagi muhim voqealar (masalan, asset nosozligi, ta'mir holati o'zgarishi, yangi vazifa tayinlanishi va hokazo) haqida foydalanuvchilarga xabar yuborish uchun ishlatiladi. Har bir xabar qaysi obyektga tegishli ekanligini va kimlarga yuborilganligini ko'rsatadi.
CREATE TABLE IF NOT EXISTS notifications (
    id UUID,
    title VARCHAR(255),                         -- Xabar sarlavhasi
    message TEXT NOT NULL,                      -- Xabar matni
    entity_type VARCHAR(100),                   -- Qaysi obyektga tegishli
    entity_id UUID,                             -- O'sha obyekt ID
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Notification recipients jadvali - bu jadvalga har bir xabar kimlarga yuborilganligi va ularning o'qilganligi haqida ma'lumot saqlanadi. Bu orqali foydalanuvchilar o'zlariga yuborilgan xabarlarni ko'rishlari va boshqarishlari mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS notification_recipients (
    notification_id UUID NOT NULL,
    user_id UUID NOT NULL,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (notification_id, user_id)
);

-- Audit loglar jadvali - bu jadval tizimda yuz berayotgan muhim harakatlarni (masalan, asset yaratish, ta'mir holati o'zgarishi, foydalanuvchi kirishi va hokazo) saqlash uchun ishlatiladi. Bu jadval tizimdagi o'zgarishlarni kuzatish, tahlil qilish va xavfsizlikni ta'minlash uchun juda muhimdir.
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID,
    actor_user_id UUID,
    entity_type VARCHAR(100),                  -- Qaysi jadval/obyekt
    entity_id UUID,                             -- Qaysi ID
    action VARCHAR(50),                         -- INSERT / UPDATE / DELETE / LOGIN / EXPORT
    old_data JSONB,                             -- Eski holat
    new_data JSONB,                             -- Yangi holat
    extra JSONB,                                -- Qo'shimcha metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Attachments jadvali - bu jadvalga asset, repair, expense yoki boshqa obyektlarga biriktirilgan fayllar (masalan, ta'mir hisoboti, xarajat kvitansiyasi, texnik pasport va hokazo) saqlanadi.
CREATE TABLE IF NOT EXISTS attachments (
    id UUID,
    entity_type VARCHAR(100) NOT NULL,         -- Qaysi obyektga biriktirilgan
    entity_id UUID NOT NULL,                    -- O'sha obyekt ID
    file_name VARCHAR(255) NOT NULL,            -- Fayl nomi
    file_url VARCHAR(2048),                     -- Fayl manzili
    content_type VARCHAR(100),
    size BIGINT,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- =========================================================
-- 12) Tashkiliy tadbirlar
-- =========================================================
-- Bu jadval texnika bilan bog'liq bo'lmagan, lekin tashkilot ichidagi muhim tadbirlar, yig'ilishlar, tekshiruvlar va boshqalar uchun ishlatiladi.
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
    end_at TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Analitik snapshotlar jadvali - bu jadval har oy yoki har chorakda texnika holati, xarajatlar va boshqa ko'rsatkichlarning umumiy ko'rinishini saqlash uchun ishlatiladi.
-- Bu jadval analitik so'rovlarni tezlashtirish va vaqt o'tishi bilan tendensiyalarni kuzatish uchun foydalidir.
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY,

    snapshot_date DATE NOT NULL,

    region_id UUID,
    service_id UUID,

    total_assets INTEGER,
    active_assets INTEGER,
    broken_assets INTEGER,
    in_repair_assets INTEGER,

    total_expenses NUMERIC(18,2),

    avg_condition_percent INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================================================
-- 13) Indekslar
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_status_code ON users(status_code);
CREATE INDEX IF NOT EXISTS idx_users_assigned_region_id ON users(assigned_region_id);
CREATE INDEX IF NOT EXISTS idx_users_assigned_service_id ON users(assigned_service_id);

CREATE INDEX IF NOT EXISTS idx_regions_parent_id ON regions(parent_id);
CREATE INDEX IF NOT EXISTS idx_asset_categories_parent_id ON asset_categories(parent_id);

CREATE INDEX IF NOT EXISTS idx_asset_models_manufacturer_id ON asset_models(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_asset_models_category_id ON asset_models(category_id);

CREATE INDEX IF NOT EXISTS idx_assets_model_id ON assets(model_id);
CREATE INDEX IF NOT EXISTS idx_assets_service_id ON assets(service_id);
CREATE INDEX IF NOT EXISTS idx_assets_region_id ON assets(region_id);
CREATE INDEX IF NOT EXISTS idx_assets_current_warehouse_id ON assets(current_warehouse_id);
CREATE INDEX IF NOT EXISTS idx_assets_status_code ON assets(status_code);
CREATE INDEX IF NOT EXISTS idx_assets_lifecycle_stage_code ON assets(lifecycle_stage_code);
CREATE INDEX IF NOT EXISTS idx_assets_responsible_user_id ON assets(responsible_user_id);

CREATE INDEX IF NOT EXISTS idx_asset_state_history_asset_id ON asset_state_history(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_transfers_asset_id ON asset_transfers(asset_id);

CREATE INDEX IF NOT EXISTS idx_warehouse_part_stock_warehouse_id ON warehouse_part_stock(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_part_stock_part_id ON warehouse_part_stock(part_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_part_movements_warehouse_id ON warehouse_part_movements(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_part_movements_part_id ON warehouse_part_movements(part_id);

CREATE INDEX IF NOT EXISTS idx_asset_parts_part_id ON asset_parts(part_id);

CREATE INDEX IF NOT EXISTS idx_repairs_asset_id ON repairs(asset_id);
CREATE INDEX IF NOT EXISTS idx_repairs_status_code ON repairs(status_code);
CREATE INDEX IF NOT EXISTS idx_repair_parts_repair_id ON repair_parts(repair_id);
CREATE INDEX IF NOT EXISTS idx_repair_parts_part_id ON repair_parts(part_id);
CREATE INDEX IF NOT EXISTS idx_repair_status_history_repair_id ON repair_status_history(repair_id);

CREATE INDEX IF NOT EXISTS idx_expenses_asset_id ON expenses(asset_id);
CREATE INDEX IF NOT EXISTS idx_expenses_repair_id ON expenses(repair_id);
CREATE INDEX IF NOT EXISTS idx_expenses_region_id ON expenses(region_id);
CREATE INDEX IF NOT EXISTS idx_expenses_service_id ON expenses(service_id);
CREATE INDEX IF NOT EXISTS idx_expenses_type_code ON expenses(expense_type_code);
CREATE INDEX IF NOT EXISTS idx_forecasts_lookup ON forecasts(region_id, service_id, asset_category_id, forecast_year);

CREATE INDEX IF NOT EXISTS idx_tasks_asset_id ON tasks(asset_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status_code ON tasks(status_code);
CREATE INDEX IF NOT EXISTS idx_notifications_entity ON notifications(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_notification_recipients_user_id_unread ON notification_recipients(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_user_id ON audit_logs(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_attachments_entity ON attachments(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_region ON analytics_snapshots(region_id);
CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_service ON analytics_snapshots(service_id);
CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_date ON analytics_snapshots(snapshot_date);
-- =========================================================
-- 14) Foreign keys
-- =========================================================

ALTER TABLE role_permissions
    ADD CONSTRAINT fk_role_permissions_role
    FOREIGN KEY (role_id) REFERENCES roles(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE role_permissions
    ADD CONSTRAINT fk_role_permissions_permission
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE users
    ADD CONSTRAINT fk_users_role
    FOREIGN KEY (role_id) REFERENCES roles(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE users
    ADD CONSTRAINT fk_users_status
    FOREIGN KEY (status_code) REFERENCES user_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE users
    ADD CONSTRAINT fk_users_region
    FOREIGN KEY (assigned_region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE users
    ADD CONSTRAINT fk_users_service
    FOREIGN KEY (assigned_service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE user_scopes
    ADD CONSTRAINT fk_user_scopes_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE user_scopes
    ADD CONSTRAINT fk_user_scopes_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE user_scopes
    ADD CONSTRAINT fk_user_scopes_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE regions
    ADD CONSTRAINT fk_regions_parent
    FOREIGN KEY (parent_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE region_services
    ADD CONSTRAINT fk_region_services_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE region_services
    ADD CONSTRAINT fk_region_services_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE asset_categories
    ADD CONSTRAINT fk_asset_categories_parent
    FOREIGN KEY (parent_id) REFERENCES asset_categories(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_models
    ADD CONSTRAINT fk_asset_models_manufacturer
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE asset_models
    ADD CONSTRAINT fk_asset_models_category
    FOREIGN KEY (category_id) REFERENCES asset_categories(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE parts
    ADD CONSTRAINT fk_parts_manufacturer
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE warehouses
    ADD CONSTRAINT fk_warehouses_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE warehouses
    ADD CONSTRAINT fk_warehouses_manager_user
    FOREIGN KEY (manager_user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE warehouse_part_stock
    ADD CONSTRAINT fk_warehouse_part_stock_warehouse
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE warehouse_part_stock
    ADD CONSTRAINT fk_warehouse_part_stock_part
    FOREIGN KEY (part_id) REFERENCES parts(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE warehouse_part_movements
    ADD CONSTRAINT fk_warehouse_part_movements_warehouse
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE warehouse_part_movements
    ADD CONSTRAINT fk_warehouse_part_movements_part
    FOREIGN KEY (part_id) REFERENCES parts(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE warehouse_part_movements
    ADD CONSTRAINT fk_warehouse_part_movements_moved_by
    FOREIGN KEY (moved_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_model
    FOREIGN KEY (model_id) REFERENCES asset_models(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_warehouse
    FOREIGN KEY (current_warehouse_id) REFERENCES warehouses(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_status
    FOREIGN KEY (status_code) REFERENCES asset_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_lifecycle_stage
    FOREIGN KEY (lifecycle_stage_code) REFERENCES lifecycle_stages(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_responsible_user
    FOREIGN KEY (responsible_user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_updated_by
    FOREIGN KEY (updated_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_deleted_by
    FOREIGN KEY (deleted_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_state_history
    ADD CONSTRAINT fk_asset_state_history_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE asset_state_history
    ADD CONSTRAINT fk_asset_state_history_status
    FOREIGN KEY (status_code) REFERENCES asset_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_state_history
    ADD CONSTRAINT fk_asset_state_history_lifecycle
    FOREIGN KEY (lifecycle_stage_code) REFERENCES lifecycle_stages(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_state_history
    ADD CONSTRAINT fk_asset_state_history_changed_by
    FOREIGN KEY (changed_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_from_region
    FOREIGN KEY (from_region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_to_region
    FOREIGN KEY (to_region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_from_service
    FOREIGN KEY (from_service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_to_service
    FOREIGN KEY (to_service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_from_warehouse
    FOREIGN KEY (from_warehouse_id) REFERENCES warehouses(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_to_warehouse
    FOREIGN KEY (to_warehouse_id) REFERENCES warehouses(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_transfers
    ADD CONSTRAINT fk_asset_transfers_transferred_by
    FOREIGN KEY (transferred_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_parts
    ADD CONSTRAINT fk_asset_parts_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE asset_parts
    ADD CONSTRAINT fk_asset_parts_part
    FOREIGN KEY (part_id) REFERENCES parts(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE asset_parts
    ADD CONSTRAINT fk_asset_parts_added_by
    FOREIGN KEY (added_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_reported_by
    FOREIGN KEY (reported_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_assigned_to
    FOREIGN KEY (assigned_to) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_performed_by
    FOREIGN KEY (performed_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_status
    FOREIGN KEY (status_code) REFERENCES repair_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_deleted_by
    FOREIGN KEY (deleted_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repair_parts
    ADD CONSTRAINT fk_repair_parts_repair
    FOREIGN KEY (repair_id) REFERENCES repairs(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE repair_parts
    ADD CONSTRAINT fk_repair_parts_part
    FOREIGN KEY (part_id) REFERENCES parts(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE repair_parts
    ADD CONSTRAINT fk_repair_parts_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repair_status_history
    ADD CONSTRAINT fk_repair_status_history_repair
    FOREIGN KEY (repair_id) REFERENCES repairs(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE repair_status_history
    ADD CONSTRAINT fk_repair_status_history_old
    FOREIGN KEY (old_status) REFERENCES repair_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repair_status_history
    ADD CONSTRAINT fk_repair_status_history_new
    FOREIGN KEY (new_status) REFERENCES repair_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repair_status_history
    ADD CONSTRAINT fk_repair_status_history_changed_by
    FOREIGN KEY (changed_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_repair
    FOREIGN KEY (repair_id) REFERENCES repairs(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_type
    FOREIGN KEY (expense_type_code) REFERENCES expense_types(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE forecasts
    ADD CONSTRAINT fk_forecasts_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE forecasts
    ADD CONSTRAINT fk_forecasts_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE forecasts
    ADD CONSTRAINT fk_forecasts_category
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE forecasts
    ADD CONSTRAINT fk_forecasts_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_status
    FOREIGN KEY (status_code) REFERENCES task_statuses(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_assigned_to
    FOREIGN KEY (assigned_to) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE notifications
    ADD CONSTRAINT fk_notifications_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE notification_recipients
    ADD CONSTRAINT fk_notification_recipients_notification
    FOREIGN KEY (notification_id) REFERENCES notifications(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE notification_recipients
    ADD CONSTRAINT fk_notification_recipients_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE audit_logs
    ADD CONSTRAINT fk_audit_logs_actor_user
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE attachments
    ADD CONSTRAINT fk_attachments_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE calendar_events
    ADD CONSTRAINT fk_calendar_events_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE analytics_snapshots
    ADD CONSTRAINT fk_analytics_snapshots_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE analytics_snapshots
    ADD CONSTRAINT fk_analytics_snapshots_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;
