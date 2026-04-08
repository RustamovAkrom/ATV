# ATV Platformasi: Polnaya Dokumentatsiya Bazy Dannykh

- Source schema: [`database.sql`](../database.sql)
- Status: aktualno po tekushchemu soderzhimomu `database.sql`

## 1. Tsel i granitsy skhemy

Eta skhema pokryvaet polnyy kontur upravleniya ATV (axborot-texnika vositalari):
- RBAC i polzovateli
- Organizatsionnaya struktura (regiony/sluzhby)
- Katalog tekhniki i klassifikatsiya
- Sklad, zapchasti i dvizheniya
- Zhiznennyy tsikl assetov
- Remont, rashody, zadachi, uvedomleniya
- Request/approval/document flow
- Audit i vlozheniya
- Snapshot-analitika

## 2. Kratkaya arkhitekturnaya karta

Osnovnaya tsepochka dannykh:

`request -> approvals -> document -> commission -> assignment/transfer -> repair -> expense -> analytics`

Vspomogatelnyye kontury:
- `users -> roles -> permissions` (bezopasnost)
- `warehouses -> parts -> stock/movements` (logistika)
- `audit_logs` i `attachments` (sled i artefakty)

## 3. Klyuchevye printsipy modeli

- Vsyudu ispolzuyutsya `UUID` PK.
- Statusy i tipy vyneseny v lookup-tablitsy (`*_statuses`, `expense_types`).
- Istoriya ne zatiskaetsya: est otdelnyye tablitsy istorii (`asset_state_history`, `repair_status_history`, `request_status_history`).
- Dlya dokumentov otdeleny:
- Zagolovok dokumenta (`documents`)
- Podpisi (`document_signatures`)
- Versii faylov (`document_files`)
- Otnosheniya `entity_type + entity_id` ispolzuyutsya kak polimorfnyy link (bez zhestkogo FK).

## 4. Modulnoye opisaniye tablits

## 4.1 RBAC i bezopasnost

### `roles`
- Naznachenie: spravochnik roley (`superadmin`, `admin`, `moderator`, `analyst`).
- Klyuchi: `id`, `name UNIQUE`.

### `permissions`
- Naznachenie: spravochnik granularnykh prav (`assets.read`, `repairs.update` i t.d.).
- Klyuchi: `id`, `code UNIQUE`.

### `role_permissions`
- Naznachenie: svyaz M:N mezhdu rolyami i pravami.
- Klyuchi: `PRIMARY KEY (role_id, permission_id)`.
- FK: na `roles`, `permissions` (cascade/cascade).

### `user_statuses`
- Naznachenie: statusy polzovateley.
- Klyuchi: `code`.

## 4.2 Organizatsionnaya struktura

### `regions`
- Naznachenie: iyerarkhiya territoriy.
- Klyuchi: `id`, `code UNIQUE`.
- Osobennosti: `parent_id` dlya dereva, `geojson` dlya geometrii.

### `services`
- Naznachenie: spravochnik napravleniy sluzhb.
- Klyuchi: `id`, `name UNIQUE`, `code UNIQUE`.

### `region_services`
- Naznachenie: svyaz M:N dostupnykh sluzhb v regione.
- Klyuchi: `PRIMARY KEY (region_id, service_id)`.

## 4.3 Polzovateli i kadrovyy profil

### `users`
- Naznachenie: akkaunt + operatsionnyy profil.
- Klyuchevyye polya:
- Avtorizatsiya: `login UNIQUE`, `password_hash`
- Profil: `first_name`, `last_name`, `position`, `badge_number UNIQUE`, `passport_number UNIQUE`
- Privyazki: `role_id`, `status_code`, `assigned_region_id`, `assigned_service_id`, `rank_id`
- Bezopasnost: `failed_login_attempts`, `is_two_factor_enabled`, `last_password_change`
- FK: na `roles`, `user_statuses`, `regions`, `services`, `ranks`.

### `ranks`
- Naznachenie: spravochnik zvanij/dolzhnostnykh urovney.
- Klyuchi: `id`, `name UNIQUE`, `code UNIQUE`.

## 4.4 Katalog tekhniki

### `asset_categories`
- Naznachenie: iyerarkhiya kategoriy tekhniki.
- Klyuchi: `id`, `code UNIQUE`.
- FK: self-link `parent_id`.

### `manufacturers`
- Naznachenie: proizvoditeli.
- Klyuchi: `id`, `name UNIQUE`.

### `asset_models`
- Naznachenie: normativnaya model tekhniki.
- Klyuchevyye polya: `manufacturer_id`, `category_id`, `lifetime_years`, `warranty_months`.
- Ogranicheniye: `UNIQUE (name, manufacturer_id)`.

### `asset_classes`
- Naznachenie: klassifikator klassov assetov (`I/II/III/IV` i t.d.).
- Klyuchi: `code`.

### `asset_class_history`
- Naznachenie: istoriya klassifikatsii asseta vo vremeni.
- Klyuchevyye polya: `asset_id`, `class_code`, `assigned_by`, `assigned_at`.
- Kommentariy: v tekushchem SQL dlya `id` ukazan `get_random_uuid()` (sm. razdel riskov).

## 4.5 Dokumenty i podpisnoy kontur

### `documents`
- Naznachenie: zagolovok/ofitsialnyy dokument bizness-protsessa.
- Klyuchevyye polya:
- `document_number UNIQUE`
- `document_type`
- `request_id` (link na request-flow)
- `status` (`draft/pending_sign/signed/cancelled`)
- `signed_by`, `signed_at` (legacy uproshchennyy kontur)
- `entity_type`, `entity_id` (polimorfnyy link)
- `file_url` (legacy, osnovnaya versiya teper v `document_files`)
- Checks:
- status v dopustimom spiske
- `signed_at` dopustim tolko pri `status='signed'`

### `document_signatures`
- Naznachenie: mnogostadiynoye/kollektivnoye podpisanie.
- Klyuchi: `UNIQUE(document_id, signer_id)`.
- Polya: `is_required`, `is_signed`, `signed_at`, `signature_type (EDS/PDF)`.

### `document_files`
- Naznachenie: versii faylov dokumenta.
- Klyuchi: `UNIQUE(document_id, version)`.
- Polya: `file_url`, `file_name`, `is_active`, `uploaded_by`.

### `warehouse_documents`
- Naznachenie: privyazka dokumenta k skladskoy operatsii (`IN/OUT`).
- Klyuchi: `UNIQUE(document_id, warehouse_id)`.
- FK: na `documents`, `warehouses`, `users(created_by)`.

## 4.6 Sklad i zapchasti

### `warehouses`
- Naznachenie: skladskie tochki.
- Klyuchevyye polya: `code UNIQUE`, `region_id`, `manager_user_id`, `is_active`.

### `parts`
- Naznachenie: katalog zapchastey.
- Klyuchi: `part_number UNIQUE`.
- FK: `manufacturer_id -> manufacturers`.

### `warehouse_part_stock`
- Naznachenie: tekushchiy ostatok po skhemu `(warehouse, part)`.
- Klyuchi: `PRIMARY KEY (warehouse_id, part_id)`.
- Checks: `quantity_on_hand >= 0`, `min_quantity >= 0`.

### `warehouse_part_movements`
- Naznachenie: zhurnal dvizheniy zapchastey.
- Polya: `movement_type (IN/OUT)`, `quantity > 0`, `reference_type`, `reference_id`, `moved_by`.

## 4.7 Assety i ikh zhiznennyy tsikl

### `assets`
- Naznachenie: glavnaya tablica tekhniki.
- Klyuchevyye polya:
- Identifikatsiya: `asset_tag UNIQUE`, `serial_number UNIQUE`
- Klassifikatsiya: `model_id`, `class_code`
- Lokatsiya: `region_id`, `service_id`, `current_warehouse_id`
- Sostoyaniye: `status_code`, `lifecycle_stage_code`, `condition_percent`
- Ekspluatatsiya: `purchase_date`, `commission_date`, `warranty_end`, `purchase_cost`, `failure_count`
- Checks: granitsy i neotritsatelnye znacheniya dlya condition/failure/usage/cost/warranty.

### `asset_state_history`
- Naznachenie: istoriya sostoyaniya asseta.
- Polya: `status_code`, `lifecycle_stage_code`, `condition_percent`, `changed_by`, `changed_at`.

### `asset_transfers`
- Naznachenie: perevody mezhdu region/service/warehouse.
- Osobennost: CHECK trebuet, chtoby hotya by odno iz napravleniy realno izmenilos.

### `asset_assignments`
- Naznachenie: fakтичесkoye zakrepleniye asseta za region/service/user.
- Polya: `assigned_to_user_id`, `transfer_id`, `assigned_at`, `unassigned_at`.
- Checks: `unassigned_at >= assigned_at`.

### `asset_parts`
- Naznachenie: komplektatsiya asseta zapchastyami.
- Klyuchi: `PRIMARY KEY (asset_id, part_id)`.

### `asset_passports`
- Naznachenie: pasportnaya karta asseta (1:1).
- Osobennost: `asset_id UNIQUE`, dop. rekvizity (`inventory_number`, `registry_number`, `production_year`).

### `asset_passport_items`
- Naznachenie: sostav pasporta (uzly/komponenty).
- Polya: `passport_id`, `name`, `serial_number`, `quantity`.

### `asset_passport_movements`
- Naznachenie: istoriya peremeshcheniy pasporta/ob"yekta.
- Polya: `from_location`, `to_location`, `document_id`, `moved_at`.

## 4.8 Remont i podryadchiki

### `vendors`
- Naznachenie: vneshniye postavshchiki/uslugi remonta.
- Polya: `name`, `contact`, `country`.

### `repairs`
- Naznachenie: karta remonta.
- Klyuchevyye polya:
- `asset_id`, `vendor_id`
- roli: `reported_by`, `assigned_to`, `performed_by`
- `status_code`, `repair_type`, `is_external`
- metrika: `total_cost`, `downtime_hours`
- Checks: neotritsatelnye `total_cost`, `downtime_hours`.

### `repair_parts`
- Naznachenie: zapchasti, ispolzovannye v remonte.
- Polya: `repair_id`, `part_id`, `quantity`, `cost`.

### `repair_status_history`
- Naznachenie: zhurnal smeny statusov remonta.
- Polya: `old_status`, `new_status`, `changed_by`, `changed_at`.

## 4.9 Rashody i operatsionnyye zadachi

### `expenses`
- Naznachenie: finansovye rashody po asset/remont/region/service.
- Polya: `expense_type_code`, `amount > 0`, `currency`, `occurred_at`.

### `tasks`
- Naznachenie: operatsionnyye zadachi po assetam i obshchiye.
- Polya: `title`, `status_code`, `assigned_to`, `due_date`.

### `notifications`
- Naznachenie: sistemnyye sobytiynye uvedomleniya.
- Polya: `entity_type`, `entity_id`, `created_by`.

### `notification_recipients`
- Naznachenie: komu otpravleno i prochitano li.
- Klyuchi: `PRIMARY KEY (notification_id, user_id)`.

## 4.10 Request/approval/commission flow

### `requests`
- Naznachenie: zayavka na deystviye (`transfer`, `repair`, `writeoff`, `procurement`).
- Polya: `status`, `request_type`, `current_step`, `is_resubmitted`, `approved_by`, `approved_at`.
- Checks:
- dopustimye statusy i tipy
- `current_step > 0`
- pri `status='approved'` obyazatelny `approved_by` i `approved_at`

### `request_items`
- Naznachenie: sostav zayavki po modelyam.
- Klyuchi: `UNIQUE(request_id, asset_model_id)`.

### `request_approvals`
- Naznachenie: shagovoye soglasovaniye.
- Klyuchi: `UNIQUE(request_id, step_order)`.
- Checks: `step_order > 0`, status v (`pending/approved/rejected`).

### `request_status_history`
- Naznachenie: istoriya statusov zayavki.

### `asset_commissions`
- Naznachenie: fiksatsiya vvedeniya/komissii asseta po dokumentu.
- Klyuchi: `UNIQUE(asset_id, document_id)`.
- Svyazi: na `assets`, `documents`, opatsionalno na `requests` i `users(commissioned_by)`.

## 4.11 Audit, vkladyvayemyye fayly i analitika

### `audit_logs`
- Naznachenie: neizmenyayemyy sled deystviy.
- Polya: `entity_type`, `entity_id`, `action`, `old_data`, `new_data`, `extra`.

### `attachments`
- Naznachenie: universalnyye fayly dlya lyubykh sushchnostey.
- Polya: `entity_type`, `entity_id`, `file_name`, `file_url`, `content_type`, `size`.

### `analytics_snapshots`
- Naznachenie: agregirovannaya periodicheskaya statistika.
- Polya: KPI po assetam i rashodam v razreze `snapshot_date/region/service`.

## 5. Karta svyazey (samoye vazhnoye)

- `users.role_id -> roles.id`
- `users.status_code -> user_statuses.code`
- `users.assigned_region_id -> regions.id`
- `users.assigned_service_id -> services.id`
- `users.rank_id -> ranks.id`

- `asset_models.manufacturer_id -> manufacturers.id`
- `asset_models.category_id -> asset_categories.id`
- `assets.model_id -> asset_models.id`
- `assets.class_code -> asset_classes.code`

- `assets.region_id -> regions.id`
- `assets.service_id -> services.id`
- `assets.current_warehouse_id -> warehouses.id`

- `repairs.asset_id -> assets.id`
- `repairs.vendor_id -> vendors.id`
- `repair_parts.repair_id -> repairs.id`
- `repair_parts.part_id -> parts.id`

- `expenses.repair_id -> repairs.id`
- `expenses.asset_id -> assets.id`

- `requests.created_by -> users.id`
- `request_items.request_id -> requests.id`
- `request_approvals.request_id -> requests.id`
- `documents.request_id -> requests.id`

- `document_signatures.document_id -> documents.id`
- `document_files.document_id -> documents.id`
- `asset_commissions.document_id -> documents.id`

## 6. Pravila tselostnosti, kotoryye uzhe est v SQL

- Kolichestvennyye proverki:
- `quantity > 0` v dvizheniyakh/zapchastyakh
- neotritsatelnye ostatki i KPI
- statusnye ENUM-like CHECK y (requests, documents, signatures)
- vremennyye proverki (`unassigned_at >= assigned_at`, `signed_at` tolko pri `signed`)

## 7. Tekushchiye riski i tocki vnimaniya (po faktu analiza)

- V tekushchem `database.sql` net blokov `CREATE INDEX`.
- Eto mozhet silno udarit po proizvoditelnosti na rostushchem ob"yeme dannykh.

- `asset_class_history.id` uses `get_random_uuid()`.
- Pri nalichii tolko `pgcrypto` obychno dostupen `gen_random_uuid()`; eto potentsialnaya oshibka migratsii.

- Dlya `asset_passports`, `asset_passport_items`, `asset_passport_movements`, `asset_class_history`, `vendors` net `IF NOT EXISTS`.
- Povtornyy zapusk skhemy mozhet padat.

- Dlya passport/history-tablits net FK-ogranicheniy.
- Vozmozhen "syroy"/orphan data bez svyazannogo `assets/documents/users`.

- V skheme smeshany `TIMESTAMP` i `TIMESTAMP WITH TIME ZONE`.
- Dlya raspredelennykh sistem luchshe standartizovat na `TIMESTAMP WITH TIME ZONE`.

## 8. Rekomenduyemyye biznes-flow (kak pravilno ispolzovat model)

- Asset transfer:
- zapis v `asset_transfers`
- zakrytie starogo assignment (`unassigned_at`)
- sozdanie novogo `asset_assignments`
- (opatsionalno) dokument v `documents` + `warehouse_documents`

- Request approval:
- sozdat `requests`
- zapolnit `request_items`
- shagovo vesti `request_approvals`
- final status + audit v `request_status_history`

- Document signing:
- sozdat `documents` (`draft`)
- dobavit marshruty podpisey v `document_signatures`
- zagruzit versii v `document_files`
- po zavershenii podpisey perevesti `documents.status -> signed`

- Repair lifecycle:
- sozdat `repairs` (`reported`)
- po mere rabot vesti `repair_status_history`
- spisat detali cherez `repair_parts`
- finansy v `expenses`

## 9. Itog

Skhema uzhe pokryvaet pochti ves ATV domain-end-to-end i stala bolee gibkoy dlya request/document/repair protsessov. Pri etom pered production-zapuskom nuzhno zakryt 4 tekhnicheskikh punkta: indexes, `get_random_uuid`, FK dlya passport-kontura, i edinaya timezone-strategiya.
