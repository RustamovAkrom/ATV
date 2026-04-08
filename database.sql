CREATE EXTENSION IF NOT EXISTS "pgcrypto";
-- Rollar jadvali - bu jadvalga tizimdagi rollar (masalan, superadmin, admin, moderator, analyst va hokazo) haqida ma'lumot saqlanadi. Har bir rol o'ziga xos nomga ega bo'ladi va bu nom rolning qaysi turga tegishli ekanligini ko'rsatadi. Bu jadval orqali rollarni boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,         -- Rol nomi: superadmin, admin, moderator, analyst
    description TEXT                           -- Rol izohi
);
-- Permissionlar jadvali - bu jadvalga tizimdagi barcha mumkin bo'lgan huquqlar (permissions) saqlanadi. Har bir permission o'ziga xos kodga ega bo'ladi va bu kod tizimdagi aniq bir harakat yoki resursga ruxsat berishni ifodalaydi. Masalan, permission kodi "assets.read" bo'lsa, bu rolga ega foydalanuvchilar texnika reyestrini o'qish huquqiga ega bo'lishadi. Bu jadval orqali rollarga kerakli huquqlarni tayinlash va boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(150) NOT NULL UNIQUE,         -- Permission kodi: assets.read, analytics.view va hokazo
    name VARCHAR(255),                         -- Odam o'qiydigan nom
    description TEXT,                          -- Batafsil izoh
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Qaysi rolga qaysi permission berilganligini ko'rsatadi. Bu jadval orqali rollarga kerakli huquqlarni tayinlash va boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID NOT NULL,                     -- Qaysi rolga beriladi
    permission_id UUID NOT NULL,               -- Qaysi permission beriladi
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Qachon berilgan
    PRIMARY KEY (role_id, permission_id)
);
-- Foydalanuvchi statuslari - bu jadvalga tizimdagi foydalanuvchilarning hozirgi holatini ko'rsatadigan statuslar saqlanadi. Har bir status o'ziga xos kodga ega bo'ladi va bu kod foydalanuvchining hozirgi holatini aniqlash uchun ishlatiladi. Masalan, foydalanuvchi statuslari "active" (faol), "blocked" (bloklangan) yoki "archived" (arxivlangan) bo'lishi mumkin. Bu jadval orqali foydalanuvchilarning holatini boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS user_statuses (
    code VARCHAR(50),
    name VARCHAR(100) NOT NULL,                -- Faol / bloklangan / arxivlangan
    description TEXT,
    PRIMARY KEY (code)
);
-- Hududlar jadvali - bu jadvalga tizimdagi hududlar (masalan, respublika, viloyat, tuman, bo'linma va hokazo) haqida ma'lumot saqlanadi. Har bir hudud o'ziga xos nomga ega bo'ladi va bu nom hududning qaysi turga tegishli ekanligini ko'rsatadi. Bu jadval orqali hududlarni boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,                -- Hudud nomi
    code VARCHAR(50) UNIQUE,                   -- Qisqa kod
    level SMALLINT,                            -- 1-respublika, 2-viloyat, 3-tuman, 4-bo'linma
    parent_id UUID,                            -- Yuqori hudud
    latitude DOUBLE PRECISION,                 -- Markaz koordinatalari
    longitude DOUBLE PRECISION,                -- Markaz koordinatalari
    geojson JSONB,                             -- Aniq hudud shakli uchun
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Xizmatlar jadvali - bu jadvalga tizimdagi xizmatlar (masalan, IT, transport, kommunal va hokazo) haqida ma'lumot saqlanadi. Har bir xizmat o'ziga xos nomga ega bo'ladi va bu nom xizmatning qaysi turga tegishli ekanligini ko'rsatadi. Bu jadval orqali xizmatlarni boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,         -- Xizmat nomi masalan, IT, transport, kommunal va hokazo
    code VARCHAR(50) UNIQUE,                   -- Xizmat kodi
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Qaysi hududda qaysi xizmatlar mavjudligini ko'rsatadi. Bu jadval orqali foydalanuvchilarga hudud va xizmatlarga asoslangan ruxsatlarni boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS region_services (
    region_id UUID NOT NULL,                   -- Hudud
    service_id UUID NOT NULL,                  -- Xizmat
    PRIMARY KEY (region_id, service_id)
);
-- =========================================================
-- 3) Foydalanuvchilar
-- =========================================================
-- Bu jadvalga tizim foydalanuvchilari haqida batafsil ma'lumot saqlanadi. Har bir foydalanuvchi o'ziga xos identifikator, login, parol, ismi, familiyasi, emaili, telefoni, roli, statusi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali foydalanuvchilarni boshqarish, ularning huquqlarini belgilash va tizimga kirishlarini nazorat qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    rank_id UUID,                            -- Lavozim
    position VARCHAR(255),                     -- Lavozim nomi (rank bilan birga ishlatiladi)
    badge_number VARCHAR(50) UNIQUE,              -- xizmat badge raqami ID
    passport_number VARCHAR(50) UNIQUE,            -- Pasport seriyasi va raqami
    hired_at DATE,                             -- Ishga qabul qilingan sana
    dismissed_at DATE,                          -- Ishdan bo'shatilgan sana
    last_login TIMESTAMP WITH TIME ZONE,       -- Oxirgi kirish vaqti
    last_password_change TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    is_two_factor_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1                 -- Optimistic locking uchun
);
CREATE TABLE IF NOT EXISTS ranks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL UNIQUE,         -- Lavozim nomi
    code VARCHAR(50) UNIQUE,                   -- Lavozim kodi
    level SMALLINT,                            -- Lavozim darajasi (1-5 gacha, 1 - eng yuqori)
    description TEXT,                          -- Lavozim izohi
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- =========================================================
-- 4) Texnika tasnifi
-- =========================================================
-- Asset kategoriyalari - bu jadvalga tizimdagi texnikalarning kategoriyalari saqlanadi. Har bir kategoriya o'ziga xos nomga ega bo'ladi va bu nom texnikaning qaysi turga tegishli ekanligini ko'rsatadi. Masalan, asset kategoriyalari "kompyuter", "server", "kamera" yoki "printer" bo'lishi mumkin. Bu jadval orqali texnikalarni kategoriyalarga ajratish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,                -- Kategoriya nomi: kompyuter, server, kamera va hokazo
    code VARCHAR(50) UNIQUE,                   -- Ichki kod
    parent_id UUID,                            -- Kategoriya ierarxiyasi
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Ishlab chiqaruvchilar jadvali - bu jadvalga har bir ishlab chiqaruvchi haqida batafsil ma'lumot saqlanadi. Har bir ishlab chiqaruvchi o'ziga xos identifikator, nomi, mamlakati, veb-sayti va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali ishlab chiqaruvchilarni boshqarish, ularning mahsulotlarini tahlil qilish va ta'minot zanjirini optimallashtirish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS manufacturers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL UNIQUE,         -- Ishlab chiqaruvchi nomi
    country VARCHAR(100),                      -- Mamlakat
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Har bir model qaysi kategoriyaga va ishlab chiqaruvchiga tegishli ekanligini ko'rsatadi. Shuningdek, normativ xizmat muddati va kafolat muddati kabi atributlar ham mavjud bo'ladi. Bu jadval orqali assetlarni standartlashtirish, tahlil qilish va prognoz qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,                -- Model nomi
    manufacturer_id UUID NOT NULL,             -- Ishlab chiqaruvchi
    category_id UUID NOT NULL,                 -- Kategoriya
    lifetime_years INTEGER,                    -- Normativ xizmat muddati
    warranty_months INTEGER,                   -- Kafolat muddati
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (name, manufacturer_id)
);
-- Hujjatlar jadvali - bu jadvalga tizimdagi hujjatlar (masalan, transfer akti, komissiya akti, ta'mir akti, hisobdan chiqarish akti va hokazo) saqlanadi. Har bir hujjat o'ziga xos identifikator, raqami, turi, kim tomonidan yaratilganligi, kim tomonidan im
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_number VARCHAR(100) NOT NULL UNIQUE,
    document_type VARCHAR(50) NOT NULL, -- TRANSFER_ACT / COMMISSION_ACT / REPAIR_ACT / WRITE_OFF_ACT

    request_id UUID, -- request oqimi bilan bog'lash uchun
    created_by UUID NOT NULL,
    signed_by UUID, -- backward compatibility: asosiy imzolovchi (ko'p imzolar document_signatures da)
    signed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft / pending_sign / signed / cancelled

    entity_type VARCHAR(100), -- Qaysi obyektga tegishli masalan: asset, repair, expense va hokazo
    entity_id UUID,                             -- O'sha obyekt ID

    file_url VARCHAR(2048), -- legacy maydon: to'liq versiyalash uchun document_files ishlatiladi

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (status IN ('draft', 'pending_sign', 'signed', 'cancelled')),
    CHECK (signed_at IS NULL OR status = 'signed')
);
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
    sort_order INTEGER DEFAULT 100,  -- Statuslarni tartibga solish uchun
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
-- Ombor jadvali - bu jadvalga har bir ombor haqida batafsil ma'lumot saqlanadi. Har bir ombor o'ziga xos identifikator, kodi, nomi, joylashuvi, mas'ul xodimi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali omborlarni boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE,                   -- Ombor kodi
    name VARCHAR(255) NOT NULL,                -- Ombor nomi
    region_id UUID,                            -- Qaysi hududdagi ombor
    manager_user_id UUID,                      -- Mas'ul xodim
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Ombor hujjatlari jadvali - bu jadvalga omborga kirim yoki chiqim harakati bilan bog'liq hujjatlar saqlanadi. Har bir hujjat o'ziga xos identifikator, kodi, turi (kirim yoki chiqim), qaysi ombor bilan bog'liq ekanligi, kim tomonidan yaratilganligi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali ombor harakatlarini boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS warehouse_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL,

    warehouse_id UUID NOT NULL,
    type VARCHAR(10) NOT NULL, -- IN / OUT

    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (type IN ('IN', 'OUT')),
    UNIQUE (document_id, warehouse_id)
);
-- Qismlar jadvali - bu jadvalga har bir qism (part) haqida batafsil ma'lumot saqlanadi. Har bir qism o'ziga xos identifikator, nomi, ishlab chiqaruvchisi, o'lchov birligi va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali qismlarni boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    part_number VARCHAR(100) UNIQUE,           -- Qism kodi/part number
    name VARCHAR(255) NOT NULL,                -- Qism nomi
    manufacturer_id UUID,                      -- Qism ishlab chiqaruvchisi
    unit VARCHAR(30) DEFAULT 'pcs',            -- O'lchov birligi
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Ombordagi qismlar qoldig'i.
-- Bu jadval parts uchun current stock holatini tez olishga yordam beradi.
CREATE TABLE IF NOT EXISTS warehouse_part_stock (
    warehouse_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0, -- Hozirgi qoldiq
    min_quantity INTEGER DEFAULT 0,              -- Minimal tavsiya etilgan qoldiq
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (quantity_on_hand >= 0),
    CHECK (min_quantity >= 0),
    PRIMARY KEY (warehouse_id, part_id)
);
-- Omborga kirim/chiqim harakati:
-- movement_type = IN yoki OUT
CREATE TABLE IF NOT EXISTS warehouse_part_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id UUID NOT NULL,
    part_id UUID NOT NULL,
    movement_type VARCHAR(10) NOT NULL,         -- IN / OUT
    quantity INTEGER NOT NULL,                  -- Miqdor
    reference_type VARCHAR(50),                 -- purchase / repair / adjustment / transfer
    reference_id UUID,                          -- Bog'langan obyekt ID
    moved_by UUID,                              -- Kim amalga oshirdi
    moved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    note TEXT,
    CHECK (movement_type IN ('IN', 'OUT')),
    CHECK (quantity > 0)
);
-- =========================================================
-- 7) Asosiy assetlar
-- =========================================================
-- Bu jadvalga har bir texnika (asset) haqida batafsil ma'lumot saqlanadi. Har bir asset o'ziga xos identifikator, modeli, joylashuvi, holati, xarid sanasi, kafolat muddati va boshqa muhim atributlarga ega bo'ladi. Bu jadval orqali assetlarni boshqarish, ularning holatini kuzatish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_tag VARCHAR(255) UNIQUE,              -- Inventar raqami
    serial_number VARCHAR(255) UNIQUE,          -- Seriya raqami
    class_code VARCHAR(50),                    -- Texnika sinfi (masalan, A, B, C)
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
    CHECK (condition_percent BETWEEN 0 AND 100),
    CHECK (failure_count >= 0),
    CHECK (usage_intensity >= 0),
    CHECK (purchase_cost IS NULL OR purchase_cost >= 0),
    CHECK (warranty_end IS NULL OR purchase_date IS NULL OR warranty_end >= purchase_date)
);
-- Asset holati tarixini saqlash.
-- Bu analitika va prognoz uchun juda muhim.
CREATE TABLE IF NOT EXISTS asset_state_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL,
    status_code VARCHAR(50),
    lifecycle_stage_code VARCHAR(50),
    condition_percent INTEGER,
    note TEXT,
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (condition_percent IS NULL OR condition_percent BETWEEN 0 AND 100)
);
-- Assetning harakat tarixi:
-- Ombordan bo'limga, bo'limdan boshqa hududga, xizmatdan omborga va hokazo.
CREATE TABLE IF NOT EXISTS asset_transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    CHECK (
        from_region_id IS DISTINCT FROM to_region_id
        OR from_service_id IS DISTINCT FROM to_service_id
        OR from_warehouse_id IS DISTINCT FROM to_warehouse_id
    )
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
    CHECK (quantity > 0),
    PRIMARY KEY (asset_id, part_id)
);
-- Assetning qaysi hududda va qaysi xizmatda ishlatilayotganini ko'rsatadi. Bu jadval orqali assetlarni joylashuv va xizmatga asoslangan boshqarish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    asset_id UUID NOT NULL,

    region_id UUID NOT NULL,
    service_id UUID NOT NULL,
    assigned_to_user_id UUID, -- amaldagi javobgar xodim
    transfer_id UUID,         -- agar transfer natijasi bo'lsa, manba yozuv

    assigned_by UUID,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    unassigned_at TIMESTAMP WITH TIME ZONE,

    note TEXT,
    CHECK (unassigned_at IS NULL OR unassigned_at >= assigned_at)
);
CREATE TABLE asset_passports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL UNIQUE,
    inventory_number VARCHAR(100) UNIQUE, -- inventar nomeri
    production_year INTEGER,
    initial_cost NUMERIC(18, 2),
    registry_number VARCHAR(100), -- reester nomeri
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE asset_passport_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passport_id UUID,
    name VARCHAR(255),
    serial_number VARCHAR(200),
    quantity INTEGER DEFAULT 1,
    note TEXT
);
CREATE TABLE asset_passport_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passport_id UUID NOT NULL,
    from_location TEXT,
    to_location TEXT,
    document_id UUID,
    moved_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE asset_class_history (
    id UUID PRIMARY KEY DEFAULT get_random_uuid(),
    asset_id UUID NOT NULL,
    class_code VARCHAR(10), -- 1, 2, 3, 4
    assigned_at TIMESTAMP DEFAULT now(),
    assigned_by UUID,
    note TEXT
);

-- Ta'mirlar jadvali - bu jadvalga har bir ta'mir operatsiyasi haqida batafsil ma'lumot saqlanadi. Har bir ta'mir qaysi texnikaga tegishli ekanligini, ta'mirni kim xabar qilganini, kimga topshirilganini, kim bajarganini, ta'mir holatini, ta'mir sanasini, ta'mir xarajatlarini va boshqa muhim ma'lumotlarni o'z ichiga oladi. Bu jadval orqali ta'mir jarayonini tahlil qilish, samaradorlikni oshirish va xarajatlarni boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS repairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL,  -- Qaysi texnikaga ta'mir qilinmoqda
    vendor_id UUID,
    reported_by UUID, -- Ta'mirni kim xabar qilgan
    assigned_to UUID,  -- Ta'mirni kimga topshirilgan
    performed_by UUID, -- Ta'mirni kim bajargan
    status_code VARCHAR(50), -- reported / in_progress / done / canceled
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    repair_date TIMESTAMP WITH TIME ZONE,  -- Ta'mir bajarilgan sana
    description TEXT,
    total_cost NUMERIC(18,2) DEFAULT 0,  -- Ta'mir xarajatlari
    is_external BOOLEAN DEFAULT false,
    downtime_hours INTEGER DEFAULT 0,  -- Ta'mir davomiyligi (soatlarda)
    repair_type VARCHAR(50), -- preventive / corrective / emergency || Ta'mir turi (preventiv yoki corrective va hokazo)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    CHECK (total_cost >= 0),
    CHECK (downtime_hours >= 0)
);
-- Ta'mirda ishlatilgan qismlar va ularning xarajatlarini saqlash. Bu ta'mir xarajatlarini tahlil qilish va qaysi qismlar eng ko'p ishlatilayotganini aniqlash uchun muhimdir.
CREATE TABLE IF NOT EXISTS repair_parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repair_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    cost NUMERIC(18,2) DEFAULT 0,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (quantity > 0),
    CHECK (cost >= 0)
);
-- Ta'mir holati o'zgarish tarixini saqlash. Bu ta'mir jarayonini tahlil qilish va samaradorlikni oshirish uchun muhimdir.
CREATE TABLE IF NOT EXISTS repair_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repair_id UUID NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Xarajatlar jadvali - bu jadvalga har bir ta'mir, transfer yoki boshqa operatsiyalar bilan bog'liq bo'lgan xarajatlar saqlanadi. Har bir xarajat qaysi assetga, ta'mirga, hududga va xizmatga tegishli ekanligini ko'rsatadi. Bu jadval orqali umumiy xarajatlarni tahlil qilish, eng ko'p xarajat qilinadigan hududlar yoki xizmatlarni aniqlash va kelgusi xarajatlarni prognoz qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    CHECK (amount > 0)
);
-- =========================================================
-- 11) Task / Notification / Audit / Attachment
-- =========================================================
-- Tasks jadvali - bu jadvalga texnika bilan bog'liq bo'lgan yoki bo'lmagan, lekin tizim ichidagi muhim vazifalar (masalan, ta'mir qilish, tekshirish, yangilash va hokazo) saqlanadi. Har bir vazifa qaysi assetga tegishli ekanligini va uning hozirgi holatini ko'rsatadi.
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID,
    title VARCHAR(250) NOT NULL,                -- Vazifa sarlavhasi
    description TEXT,
    status_code VARCHAR(50),
    assigned_to UUID,
    due_date TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Notifications jadvali - bu jadval tizimdagi muhim voqealar (masalan, asset nosozligi, ta'mir holati o'zgarishi, yangi vazifa tayinlanishi va hokazo) haqida foydalanuvchilarga xabar yuborish uchun ishlatiladi. Har bir xabar qaysi obyektga tegishli ekanligini va kimlarga yuborilganligini ko'rsatadi.
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255),                         -- Xabar sarlavhasi
    message TEXT NOT NULL,                      -- Xabar matni
    entity_type VARCHAR(100),                   -- Qaysi obyektga tegishli masalan: asset, repair, expense va hokazo
    entity_id UUID,                             -- O'sha obyekt ID
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID,
    entity_type VARCHAR(100),                  -- Qaysi jadval/obyekt
    entity_id UUID,                             -- Qaysi ID
    action VARCHAR(50),                         -- INSERT / UPDATE / DELETE / LOGIN / EXPORT
    old_data JSONB,                             -- Eski holat
    new_data JSONB,                             -- Yangi holat
    extra JSONB,                                -- Qo'shimcha metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Attachments jadvali - bu jadvalga asset, repair, expense yoki boshqa obyektlarga biriktirilgan fayllar (masalan, ta'mir hisoboti, xarajat kvitansiyasi, texnik pasport va hokazo) saqlanadi.
CREATE TABLE IF NOT EXISTS attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,         -- Qaysi obyektga biriktirilgan
    entity_id UUID NOT NULL,                    -- O'sha obyekt ID
    file_name VARCHAR(255) NOT NULL,            -- Fayl nomi
    file_url VARCHAR(2048),                     -- Fayl manzili
    content_type VARCHAR(100),
    size BIGINT,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (size IS NULL OR size >= 0)
);

-- Analitik snapshotlar jadvali - bu jadval har oy yoki har chorakda texnika holati, xarajatlar va boshqa ko'rsatkichlarning umumiy ko'rinishini saqlash uchun ishlatiladi.
-- Bu jadval analitik so'rovlarni tezlashtirish va vaqt o'tishi bilan tendensiyalarni kuzatish uchun foydalidir.
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    snapshot_date DATE NOT NULL,

    region_id UUID,
    service_id UUID,

    total_assets INTEGER, -- Umumiy assetlar soni
    active_assets INTEGER, -- Faol assetlar soni
    broken_assets INTEGER, -- Nosoz assetlar soni
    in_repair_assets INTEGER, -- Ta'mirda bo'lgan assetlar soni

    total_expenses NUMERIC(18,2),

    avg_condition_percent INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    CHECK (total_assets IS NULL OR total_assets >= 0),
    CHECK (active_assets IS NULL OR active_assets >= 0),
    CHECK (broken_assets IS NULL OR broken_assets >= 0),
    CHECK (in_repair_assets IS NULL OR in_repair_assets >= 0),
    CHECK (total_expenses IS NULL OR total_expenses >= 0),
    CHECK (avg_condition_percent IS NULL OR avg_condition_percent BETWEEN 0 AND 100)
);
-- Assetga ta'mir yoki transfer uchun ruxsat so'rovlarini saqlash. Bu jadval orqali assetga ta'mir yoki transfer qilishdan oldin ruxsat olish jarayonini boshqarish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    created_by UUID NOT NULL, -- Ruxsat so'rovini kim yaratgan
    region_id UUID NOT NULL, -- Qaysi hududga tegishli
    service_id UUID NOT NULL, -- Qaysi xizmatga tegishli

    status VARCHAR(50) DEFAULT 'pending', -- pending / approved / rejected
    request_type VARCHAR(50) DEFAULT 'transfer', -- transfer / repair / writeoff / procurement
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,

    current_step SMALLINT DEFAULT 1, -- Hozirgi tasdiqlash bosqichi
    is_resubmitted BOOLEAN DEFAULT false, -- Qayta yuborilganmi

    comment TEXT, -- Ruxsat berish yoki rad etish uchun izoh

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    CHECK (request_type IN ('transfer', 'repair', 'writeoff', 'procurement')),
    CHECK (current_step > 0),
    CHECK (
        (status = 'approved' AND approved_by IS NOT NULL AND approved_at IS NOT NULL)
        OR (status <> 'approved')
    )
);

-- Request itemlar jadvali - bu jadvalga har bir ruxsat so'roviga tegishli bo'lgan itemlar saqlanadi. Har bir item qaysi asset modeliga tegishli ekanligini va necha dona kerakligini ko'rsatadi. Bu jadval orqali ruxsat so'rovlarini batafsil boshqarish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS request_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    request_id UUID NOT NULL,
    asset_model_id UUID NOT NULL,

    quantity INTEGER NOT NULL DEFAULT 1, -- Nechta asset kerak
    note TEXT,
    CHECK (quantity > 0),
    UNIQUE (request_id, asset_model_id)
);
-- Assetga ta'mir yoki transfer qilish uchun ruxsat berilgan holatlarni saqlash. Bu jadval orqali assetga ta'mir yoki transfer qilish jarayonini boshqarish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    asset_id UUID NOT NULL,
    document_id UUID NOT NULL,
    request_id UUID,
    commissioned_by UUID,

    commissioned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Ta'mir yoki transfer qachon amalga oshirilgan

    note TEXT,
    UNIQUE (asset_id, document_id)
);

-- Ruxsat so'rovlarini tasdiqlash jarayonini boshqarish uchun jadval. Har bir ruxsat so'roviga bir nechta tasdiqlash bosqichlari bo'lishi mumkin (masalan, hudud rahbari, xizmat rahbari, moliya bo'limi va hokazo). Bu jadval orqali ruxsat so'rovlarini batafsil boshqarish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS request_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    request_id UUID NOT NULL,
    step_order SMALLINT NOT NULL, -- 1,2,...

    approver_id UUID NOT NULL,

    status VARCHAR(50) DEFAULT 'pending', -- pending/approved/rejected

    comment TEXT,

    acted_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(request_id, step_order),
    CHECK (step_order > 0),
    CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- Ruxsat so'rovlarining holat o'zgarish tarixini saqlash. Bu jadval orqali ruxsat so'rovlarining holat o'zgarishlarini tahlil qilish va jarayonni optimallashtirish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS request_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    request_id UUID NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),

    changed_by UUID,
    changed_at TIMESTAMP DEFAULT NOW(),
    CHECK (new_status IS NULL OR new_status IN ('pending', 'approved', 'rejected', 'cancelled'))
);

-- Hujjat imzolash jarayonini boshqarish uchun jadval. Ba'zi hujjatlar (masalan, transfer akti, komissiya akti va hokazo) imzolanishi kerak bo'lishi mumkin. Bu jadval orqali hujjat imzolash jarayonini boshqarish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS document_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL,
    signer_id UUID NOT NULL,

    role VARCHAR(50), -- chairman/member

    is_required BOOLEAN DEFAULT true,
    is_signed BOOLEAN DEFAULT false,

    signed_at TIMESTAMP WITH TIME ZONE,
    signature_type VARCHAR(20), -- EDS / PDF

    UNIQUE(document_id, signer_id),
    CHECK (signature_type IS NULL OR signature_type IN ('EDS', 'PDF')),
    CHECK ((is_signed = true AND signed_at IS NOT NULL) OR (is_signed = false))
);

-- Hujjatga biriktirilgan fayllar jadvali. Ba'zi hujjatlar bilan bir nechta fayllar (masalan, ta'mir hisoboti, xarajat kvitansiyasi va hokazo) biriktirilishi mumkin. Bu jadval orqali hujjatga biriktirilgan fayllarni boshqarish va tahlil qilish mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS document_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL,

    file_url TEXT NOT NULL,
    file_name VARCHAR(255),
    version INTEGER DEFAULT 1,

    uploaded_by UUID,
    uploaded_at TIMESTAMP DEFAULT NOW(),

    is_active BOOLEAN DEFAULT true,
    CHECK (version > 0),
    UNIQUE (document_id, version)
);
-- Asset klasslari jadvali - bu jadvalga tizimdagi texnikalarning asosiy turlarini ko'rsatadigan kodlar saqlanadi. Har bir asset klassi o'ziga xos kodga ega bo'ladi va bu kod texnikaning qaysi turga tegishli ekanligini aniqlash uchun ishlatiladi. Masalan, asset klasslari "I" (kompyuterlar), "II" (ofis uskunalari), "III" (transport vositalari) yoki "IV" (boshqa) bo'lishi mumkin. Bu jadval orqali texnikalarni asosiy turlarga ajratish, tahlil qilish va hisobotlar tayyorlash mumkin bo'ladi.
CREATE TABLE IF NOT EXISTS asset_classes (
    code VARCHAR(10) PRIMARY KEY, -- I, II, III, IV
    name VARCHAR(100) NOT NULL
);
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    contact TEXT,
    country VARCHAR(100)
);

-- =========================================================
-- Foreign keys
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

ALTER TABLE users
    ADD CONSTRAINT fk_users_rank
    FOREIGN KEY (rank_id) REFERENCES ranks(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

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

ALTER TABLE warehouse_documents
    ADD CONSTRAINT fk_warehouse_documents_document
    FOREIGN KEY (document_id) REFERENCES documents(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE warehouse_documents
    ADD CONSTRAINT fk_warehouse_documents_warehouse
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE warehouse_documents
    ADD CONSTRAINT fk_warehouse_documents_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

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

ALTER TABLE asset_assignments
    ADD CONSTRAINT fk_asset_assignments_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE asset_assignments
    ADD CONSTRAINT fk_asset_assignments_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE asset_assignments
    ADD CONSTRAINT fk_asset_assignments_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE asset_assignments
    ADD CONSTRAINT fk_asset_assignments_assigned_by
    FOREIGN KEY (assigned_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_assignments
    ADD CONSTRAINT fk_asset_assignments_assigned_to_user
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_assignments
    ADD CONSTRAINT fk_asset_assignments_transfer
    FOREIGN KEY (transfer_id) REFERENCES asset_transfers(id)
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
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE analytics_snapshots
    ADD CONSTRAINT fk_analytics_snapshots_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE analytics_snapshots
    ADD CONSTRAINT fk_analytics_snapshots_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE requests
    ADD CONSTRAINT fk_requests_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE requests
    ADD CONSTRAINT fk_requests_region
    FOREIGN KEY (region_id) REFERENCES regions(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE requests
    ADD CONSTRAINT fk_requests_service
    FOREIGN KEY (service_id) REFERENCES services(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE requests
    ADD CONSTRAINT fk_requests_approved_by
    FOREIGN KEY (approved_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE request_items
    ADD CONSTRAINT fk_request_items_request
    FOREIGN KEY (request_id) REFERENCES requests(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE request_items
    ADD CONSTRAINT fk_request_items_model
    FOREIGN KEY (asset_model_id) REFERENCES asset_models(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE request_approvals
    ADD CONSTRAINT fk_request_approvals_request
    FOREIGN KEY (request_id) REFERENCES requests(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE request_approvals
    ADD CONSTRAINT fk_request_approvals_approver
    FOREIGN KEY (approver_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE request_status_history
    ADD CONSTRAINT fk_request_status_history_request
    FOREIGN KEY (request_id) REFERENCES requests(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE request_status_history
    ADD CONSTRAINT fk_request_status_history_changed_by
    FOREIGN KEY (changed_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_commissions
    ADD CONSTRAINT fk_asset_commissions_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE asset_commissions
    ADD CONSTRAINT fk_asset_commissions_document
    FOREIGN KEY (document_id) REFERENCES documents(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE asset_commissions
    ADD CONSTRAINT fk_asset_commissions_request
    FOREIGN KEY (request_id) REFERENCES requests(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE asset_commissions
    ADD CONSTRAINT fk_asset_commissions_commissioned_by
    FOREIGN KEY (commissioned_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE documents
    ADD CONSTRAINT fk_documents_request
    FOREIGN KEY (request_id) REFERENCES requests(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE documents
    ADD CONSTRAINT fk_documents_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE documents
    ADD CONSTRAINT fk_documents_signed_by
    FOREIGN KEY (signed_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE document_signatures
    ADD CONSTRAINT fk_document_signatures_document
    FOREIGN KEY (document_id) REFERENCES documents(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE document_signatures
    ADD CONSTRAINT fk_document_signatures_signer
    FOREIGN KEY (signer_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE document_files
    ADD CONSTRAINT fk_document_files_document
    FOREIGN KEY (document_id) REFERENCES documents(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE document_files
    ADD CONSTRAINT fk_document_files_uploaded_by
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE assets
    ADD CONSTRAINT fk_assets_class
    FOREIGN KEY (class_code) REFERENCES asset_classes(code)
    ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE repairs
    ADD CONSTRAINT fk_repairs_vendor
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
    ON UPDATE CASCADE ON DELETE SET NULL;
