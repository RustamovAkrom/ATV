# Production deploy

Руководство описывает деплой проекта на чистый Ubuntu 22.04/24.04 сервер через Docker Compose и production-профиль `prod`.

## 1. Что запускается в production

`docker-compose.yml` поднимает:

- `web` - FastAPI backend. При старте ждёт PostgreSQL, применяет `alembic upgrade head`, затем при `ENV=prod` запускается через Gunicorn + Uvicorn workers.
- `postgres` - PostgreSQL 16 с volume `pg_data`.
- `redis` - Redis 7 с volume `redis_data`.
- `celery_worker`, `celery_beat`, `celery_flower` - фоновые задачи и Flower.
- `nginx` - reverse proxy, статические файлы и `/storage`, включается только через profile `prod` или `nginx`.

Важно: production-настройки nginx в `deployments/compose/nginx/conf.d/default.conf` должны быть включены только на сервере. Для локальной разработки оставляйте активным `LOCAL MODE` или запускайте без `--profile prod`.

## 2. Подготовка сервера

Подключитесь к серверу:

```bash
ssh root@YOUR_SERVER_IP
```

Обновите систему:

```bash
apt update
apt upgrade -y
apt install -y ca-certificates curl gnupg lsb-release git ufw
```

Откройте порты:

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

## 3. Установка Docker и Docker Compose

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

docker --version
docker compose version
```

Если деплой выполняется не от `root`, добавьте пользователя в группу Docker и перелогиньтесь:

```bash
usermod -aG docker $USER
```

## 4. Клонирование репозитория

```bash
mkdir -p /opt/iibatv
cd /opt/iibatv
git clone YOUR_REPOSITORY_URL .
```

Проверьте, что на сервере нужная ветка:

```bash
git status
git branch --show-current
```

## 5. Настройка `.env`

Создайте production `.env` из примера:

```bash
cp .env-example .env
nano .env
```

Пример production-конфига:

```dotenv
ENV=prod
DEBUG=false
SECRET_KEY=replace-with-long-random-secret

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=iibatv
POSTGRES_PASSWORD=replace-with-strong-db-password
POSTGRES_DB=iibatv
POSTGRES_ECHO=false

ALLOWED_HOSTS=example.com,www.example.com,localhost,127.0.0.1
CORS_ORIGINS=https://example.com,https://www.example.com

JWT_ISSUER=iibatv
JWT_AUDIENCE=fastapi-client
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

RATE_LIMIT_ENABLED=true
RATE_LIMIT_STORAGE_URL=redis://redis:6379/0
RATE_LIMIT_DEFAULT=10/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_TRUSTED_PROXIES=

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TIMEZONE=Asia/Tashkent

REDIS_URL=redis://redis:6379/0

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM=noreply@example.com
SMTP_USER=noreply@example.com
SMTP_PASSWORD=replace-with-smtp-password

SENTRY_DSN=
PROMETHEUS_METRICS_KEY=

LOG_INCLUDE_REQUEST_ID=true
LOG_LEVEL=INFO
LOG_JSON=true
LOG_ENQUEUE=false
SERVICE_NAME=iibatv-backend

AUDIT_ENABLED=true

STORAGE_ROOT_DIR=storage
STORAGE_URL_PREFIX=https://example.com/storage
STORAGE_DEFAULT_MAX_SIZE_MB=10
STORAGE_DEFAULT_ALLOWED_MIMETYPES=image/jpeg,image/png,image/gif,image/webp,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document
STORAGE_AVATAR_MAX_SIZE_MB=2
STORAGE_AVATAR_ALLOWED_MIMETYPES=image/jpeg,image/jpg,image/png,image/gif,image/webp
STORAGE_AVATAR_FOLDER=avatars
STORAGE_ASSET_IMAGE_MAX_SIZE_MB=5
STORAGE_ASSET_IMAGE_ALLOWED_MIMETYPES=image/jpeg,image/png,image/gif,image/webp
STORAGE_ASSET_IMAGE_FOLDER=assets
STORAGE_DOCUMENT_MAX_SIZE_MB=15
STORAGE_DOCUMENT_ALLOWED_MIMETYPES=application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
STORAGE_DOCUMENT_FOLDER=documents
STORAGE_FILENAME_MAX_LENGTH=255
STORAGE_KEEP_ORIGINAL_NAME=false
STORAGE_VIRUS_SCAN_ENABLED=false
STORAGE_VIRUS_SCAN_URL=

APP_HOST=0.0.0.0
APP_PORT=8000
WORKERS=4
POSTGRES_TIMEOUT=60
```

Сгенерировать `SECRET_KEY` можно так:

```bash
openssl rand -hex 32
```

Примечания:

- `POSTGRES_HOST` внутри Docker должен быть `postgres`, не `localhost`.
- `ALLOWED_HOSTS` должен содержать production-домен. Иначе `TrustedHostMiddleware` может отдавать 400.
- `CORS_ORIGINS` должен содержать только реальные frontend origins.
- В `.env-example` есть старые `UPLOAD_*` переменные; текущий backend читает `STORAGE_*`.
- Не коммитьте `.env`, SSL-ключи и backup-файлы.

## 6. Настройка домена и DNS

В DNS панели домена создайте записи:

```text
A      example.com       YOUR_SERVER_IP
A      www.example.com   YOUR_SERVER_IP
```

Если используется IPv6:

```text
AAAA   example.com       YOUR_SERVER_IPV6
AAAA   www.example.com   YOUR_SERVER_IPV6
```

Проверьте, что DNS уже указывает на сервер:

```bash
dig +short example.com
dig +short www.example.com
```

## 7. Получение SSL сертификатов Let's Encrypt

Установите Certbot на хост:

```bash
apt install -y certbot
```

На время получения сертификата порт 80 должен быть свободен. Если контейнеры уже запущены, остановите nginx или весь compose:

```bash
docker compose --profile prod stop nginx || true
```

Получите сертификат:

```bash
certbot certonly --standalone -d example.com -d www.example.com
```

`docker-compose.yml` монтирует SSL в контейнер из `./deployments/compose/nginx/nginx/ssl` в `/etc/nginx/ssl`, поэтому скопируйте сертификаты именно туда:

```bash
mkdir -p deployments/compose/nginx/nginx/ssl
cp /etc/letsencrypt/live/example.com/fullchain.pem deployments/compose/nginx/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/example.com/privkey.pem deployments/compose/nginx/nginx/ssl/key.pem
chmod 600 deployments/compose/nginx/nginx/ssl/key.pem
```

## 8. Активация production режима Nginx

Откройте конфиг:

```bash
nano deployments/compose/nginx/conf.d/default.conf
```

Сделайте изменения:

- закомментируйте блок `# LOCAL MODE (enabled by default)` с `listen 80; server_name _;`;
- раскомментируйте блок `# PROD MODE`;
- замените `server_name _;` на реальные домены, например `server_name example.com www.example.com;`;
- оставьте `ssl_certificate /etc/nginx/ssl/cert.pem;`;
- оставьте `ssl_certificate_key /etc/nginx/ssl/key.pem;`.

Итоговая production-логика должна быть такой:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    resolver 127.0.0.11 ipv6=off valid=10s;
    set $backend "web:8000";

    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;

    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /storage/ {
        alias /app/storage/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://$backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Проверьте конфиг после запуска контейнера командой из секции troubleshooting.

## 9. Запуск production

Соберите и запустите сервисы:

```bash
docker compose --profile prod up -d --build
```

Проверьте статус:

```bash
docker compose --profile prod ps
```

Проверьте healthcheck:

```bash
curl -I http://localhost/healthcheck
curl -I https://example.com/healthcheck
```

## 10. Миграции, bootstrap и superadmin

Контейнер `web` автоматически выполняет:

```bash
alembic upgrade head
```

при каждом старте. При необходимости применить миграции вручную:

```bash
docker compose exec web alembic -c /app/alembic.ini upgrade head
```

Инициализируйте роли и права:

```bash
docker compose exec web python -m scripts.cli bootstrap
```

Создайте superadmin:

```bash
docker compose exec web python -m scripts.cli create-superadmin
```

Команда интерактивно спросит `Login`, `Password`, `Email`, `Phone`. После этого админка будет доступна по:

```text
https://example.com/admin
```

## 11. Полезные команды эксплуатации

### Логи

Все сервисы:

```bash
docker compose --profile prod logs -f --tail=200
```

Отдельные сервисы:

```bash
docker compose logs -f --tail=200 web
docker compose logs -f --tail=200 nginx
docker compose logs -f --tail=200 postgres
docker compose logs -f --tail=200 celery_worker
docker compose logs -f --tail=200 celery_beat
```

### Перезапуск сервисов

```bash
docker compose --profile prod restart
docker compose restart web
docker compose restart nginx
docker compose restart celery_worker celery_beat
```

### Остановка и запуск

```bash
docker compose --profile prod stop
docker compose --profile prod up -d
```

Не используйте `docker compose down -v` на production: флаг `-v` удалит volumes базы данных и Redis.

### Backup базы данных

```bash
mkdir -p backups
set -a
source .env
set +a
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "backups/postgres-$(date +%F-%H%M%S).sql"
```

Сжатый backup:

```bash
mkdir -p backups
set -a
source .env
set +a
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "backups/postgres-$(date +%F-%H%M%S).sql.gz"
```

Восстановление из plain SQL backup:

```bash
set -a
source .env
set +a
docker compose exec -T postgres psql -U "$POSTGRES_USER" "$POSTGRES_DB" < backups/postgres-YYYY-MM-DD-HHMMSS.sql
```

Перед восстановлением на production сделайте свежий backup.

### Обновление кода на сервере

```bash
cd /opt/iibatv
git fetch origin
git status
git pull --ff-only
docker compose --profile prod up -d --build
docker compose --profile prod ps
docker compose logs -f --tail=100 web
```

Если были изменения в nginx-конфиге:

```bash
docker compose exec nginx nginx -t
docker compose restart nginx
```

### Обновление SSL сертификатов

Проверить dry-run:

```bash
certbot renew --dry-run
```

Обновить сертификаты и скопировать их в volume-путь nginx:

```bash
certbot renew
cp /etc/letsencrypt/live/example.com/fullchain.pem deployments/compose/nginx/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/example.com/privkey.pem deployments/compose/nginx/nginx/ssl/key.pem
chmod 600 deployments/compose/nginx/nginx/ssl/key.pem
docker compose restart nginx
```

Для автоматизации создайте hook:

```bash
nano /etc/letsencrypt/renewal-hooks/deploy/iibatv-nginx.sh
```

Содержимое:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/iibatv"
DOMAIN="example.com"

cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${PROJECT_DIR}/deployments/compose/nginx/nginx/ssl/cert.pem"
cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" "${PROJECT_DIR}/deployments/compose/nginx/nginx/ssl/key.pem"
chmod 600 "${PROJECT_DIR}/deployments/compose/nginx/nginx/ssl/key.pem"

cd "${PROJECT_DIR}"
docker compose restart nginx
```

Активируйте hook:

```bash
chmod +x /etc/letsencrypt/renewal-hooks/deploy/iibatv-nginx.sh
```

## 12. Troubleshooting

### `nginx` не стартует из-за сертификатов

Проверьте, что файлы существуют в пути, который монтируется в `docker-compose.yml`:

```bash
ls -la deployments/compose/nginx/nginx/ssl
docker compose exec nginx nginx -t
docker compose logs --tail=100 nginx
```

Внутри контейнера должны быть:

```text
/etc/nginx/ssl/cert.pem
/etc/nginx/ssl/key.pem
```

### 400 Bad Request на домене

Скорее всего домен отсутствует в `ALLOWED_HOSTS`.

Проверьте `.env`:

```dotenv
ALLOWED_HOSTS=example.com,www.example.com,localhost,127.0.0.1
```

Затем перезапустите backend:

```bash
docker compose restart web
```

### CORS ошибки в браузере

Добавьте frontend origin в `CORS_ORIGINS`:

```dotenv
CORS_ORIGINS=https://example.com,https://www.example.com
```

Перезапустите backend:

```bash
docker compose restart web
```

### `web` ждёт PostgreSQL и не стартует

Проверьте healthcheck и переменные:

```bash
docker compose ps postgres
docker compose logs --tail=100 postgres
docker compose logs --tail=100 web
```

В `.env` для Docker должно быть:

```dotenv
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

### Миграции падают при старте

Посмотрите ошибку:

```bash
docker compose logs --tail=200 web
```

Проверьте подключение к базе:

```bash
docker compose exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Попробуйте применить миграции вручную:

```bash
docker compose exec web alembic -c /app/alembic.ini upgrade head
```

### `create-superadmin` пишет, что roles не initialized

Сначала выполните bootstrap:

```bash
docker compose exec web python -m scripts.cli bootstrap
docker compose exec web python -m scripts.cli create-superadmin
```

### 502 Bad Gateway

Проверьте, жив ли backend:

```bash
docker compose ps web
docker compose logs --tail=100 web
docker compose exec nginx wget -q -O - http://web:8000/healthcheck
```

Если backend не проходит healthcheck, сначала исправьте ошибку в логах `web`, затем перезапустите:

```bash
docker compose restart web nginx
```

### Статика или storage не открываются

Проверьте директории на хосте:

```bash
ls -la src/static
ls -la src/storage
```

В `docker-compose.yml` nginx монтирует:

```text
./src/static:/app/static:ro
./src/storage:/app/storage:ro
```

Проверьте `STORAGE_URL_PREFIX`:

```dotenv
STORAGE_URL_PREFIX=https://example.com/storage
```

### Certbot не может получить сертификат

Проверьте DNS, firewall и свободный порт 80:

```bash
dig +short example.com
ufw status
ss -tulpn | grep ':80'
```

Если порт занят nginx-контейнером:

```bash
docker compose stop nginx
certbot certonly --standalone -d example.com -d www.example.com
docker compose --profile prod up -d nginx
```

### Локальная разработка сломалась после production-настроек nginx

Для локальной разработки не включайте production nginx:

```bash
docker compose up -d postgres redis
```

Или верните `deployments/compose/nginx/conf.d/default.conf` к локальному режиму:

- `LOCAL MODE` раскомментирован;
- `PROD MODE` закомментирован;
- `.env` содержит `ENV=local` или `ENV=dev`, `DEBUG=true`.

Production режим backend включается только при:

```dotenv
ENV=prod
```

а nginx-контейнер поднимается только при:

```bash
docker compose --profile prod up -d
```
