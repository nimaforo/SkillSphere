# 🐘 PostgreSQL Migration Guide

## ✅ تکمیل شده

SQLite سے PostgreSQL میں مکمل migration setup!

---

## 📁 فائلیں بنایا گیا

### 1. **`.env.example`**
```bash
تمام environment variables کے لیے template
```

### 2. **`.env.development`**
```bash
Development environment setup
```

### 3. **`requirements.txt`**
```bash
✅ psycopg2-binary - PostgreSQL adapter
✅ python-dotenv - Environment variables
✅ Pillow - Image processing
✅ تمام دوسرے dependencies
```

### 4. **`docker-compose.yml`**
```yaml
✅ PostgreSQL 16 service
✅ Redis service
✅ Django application
✅ Celery worker
✅ Celery beat
✅ Flower monitoring
```

### 5. **`Dockerfile`**
```dockerfile
✅ Python 3.11-slim
✅ System dependencies
✅ Python packages
```

### 6. **`core/settings.py`** (Updated)
```python
✅ Environment variables support
✅ PostgreSQL configuration
✅ Security settings
✅ CORS restrictions
✅ Cache configuration
```

---

## 🚀 شروع کرنا

### Option 1: Docker Compose (Recommended)

#### Step 1: Environment Files
```bash
# .env فائل بنائیں
cp .env.example .env

# یا development کے لیے
cp .env.development .env
```

#### Step 2: Docker Start
```bash
# تمام services شروع کریں
docker-compose up -d

# Logs دیکھیں
docker-compose logs -f django

# Status چیک کریں
docker-compose ps
```

#### Step 3: Migrations
```bash
# Migrations اطلاق کریں
docker-compose exec django python manage.py migrate

# Superuser بنائیں
docker-compose exec django python manage.py createsuperuser
```

#### Step 4: Access
```
Django: http://localhost:8000
Admin: http://localhost:8000/admin
Flower: http://localhost:5555
```

---

### Option 2: Local Setup

#### Step 1: PostgreSQL Install

**Windows:**
```bash
choco install postgresql
# یا Download: https://www.postgresql.org/download/windows/
```

**macOS:**
```bash
brew install postgresql
```

**Ubuntu:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

#### Step 2: Create Database
```bash
# PostgreSQL prompt میں
psql -U postgres

# Database بنائیں
CREATE DATABASE skillsphere;
CREATE USER skillsphere_user WITH PASSWORD 'skillsphere_password';
ALTER ROLE skillsphere_user SET client_encoding TO 'utf8';
ALTER ROLE skillsphere_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE skillsphere_user SET default_transaction_deferrable TO on;
ALTER ROLE skillsphere_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE skillsphere TO skillsphere_user;
\q
```

#### Step 3: Environment Setup
```bash
# .env بنائیں
copy .env.example .env

# Database credentials update کریں
DB_ENGINE=django.db.backends.postgresql
DB_NAME=skillsphere
DB_USER=skillsphere_user
DB_PASSWORD=skillsphere_password
DB_HOST=localhost
DB_PORT=5432
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### Step 6: Run Server
```bash
python manage.py runserver
```

---

## 🔧 Migration Process (SQLite → PostgreSQL)

### Step 1: Backup SQLite
```bash
# موجودہ SQLite dump کریں
python manage.py dumpdata > backup.json
```

### Step 2: PostgreSQL Setup
```bash
# Database اور user بنائیں
createdb -U postgres -h localhost skillsphere
```

### Step 3: Update Settings
```python
# core/settings.py میں database configuration update کریں
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "skillsphere",
        "USER": "skillsphere_user",
        "PASSWORD": "your-password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Restore Data (Optional)
```bash
# اگر پرانے ڈیٹا کو restore کرنا ہو
python manage.py loaddata backup.json
```

---

## 📊 PostgreSQL Configuration

### Connection Pooling (Production)
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "CONN_MAX_AGE": 600,  # 10 minutes
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# یا pgBouncer استعمال کریں
```

### Backup Strategy
```bash
# Daily backup
pg_dump skillsphere -U skillsphere_user -h localhost > backup_$(date +%Y%m%d).sql

# Restore
psql skillsphere -U skillsphere_user -h localhost < backup_20240723.sql
```

---

## 🐳 Docker Commands

### Start Services
```bash
# Background میں شروع کریں
docker-compose up -d

# Foreground (logs دیکھنے کے لیے)
docker-compose up
```

### Stop Services
```bash
docker-compose down

# تمام volumes ڈیٹا کے ساتھ حذف کریں
docker-compose down -v
```

### View Logs
```bash
# تمام services
docker-compose logs

# ایک specific service
docker-compose logs django
docker-compose logs postgres

# Real-time logs
docker-compose logs -f django
```

### Execute Commands
```bash
# Django management command
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
docker-compose exec django python manage.py shell

# PostgreSQL command
docker-compose exec postgres psql -U skillsphere_user -d skillsphere

# Celery status
docker-compose exec celery_worker celery -A core inspect active
```

### Database Operations
```bash
# Backup
docker-compose exec postgres pg_dump -U skillsphere_user skillsphere > backup.sql

# Restore
docker-compose exec -T postgres psql -U skillsphere_user skillsphere < backup.sql

# CLI میں جائیں
docker-compose exec postgres psql -U skillsphere_user -d skillsphere
```

---

## ⚙️ Environment Variables

### Required
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=skillsphere
DB_USER=skillsphere_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost  # or postgres (Docker)
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

### Optional
```bash
DEBUG=True
SECRET_KEY=your-secret-key
CELERY_BROKER_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 🔍 Common Issues

### Issue: Connection refused
```
FATAL: Ident authentication failed for user "skillsphere_user"
```
**حل:**
```bash
# pg_hba.conf میں authentication method تبدیل کریں
# /etc/postgresql/16/main/pg_hba.conf

# اس لائن کو:
local   all             all                                     ident
# کریں:
local   all             all                                     md5
# یا:
local   all             all                                     trust
```

### Issue: Database does not exist
```
FATAL: database "skillsphere" does not exist
```
**حل:**
```bash
# Database بنائیں
createdb -U postgres skillsphere
```

### Issue: Role does not exist
```
FATAL: role "skillsphere_user" does not exist
```
**حل:**
```bash
# User بنائیں
psql -U postgres -c "CREATE USER skillsphere_user WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skillsphere TO skillsphere_user;"
```

### Issue: Docker network issues
```
ERROR: No such service: postgres
```
**حل:**
```bash
# Network بنائیں
docker-compose down
docker-compose up -d
```

---

## 📊 Performance Monitoring

### Database Stats
```bash
# PostgreSQL میں
SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database;

# Table sizes
SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Query Performance
```bash
# Slow queries enable کریں
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

# Connection count
SELECT count(*) FROM pg_stat_activity;
```

---

## 🔐 Security Checklist

- [ ] PostgreSQL password secure ہے
- [ ] ALLOWED_HOSTS محدود ہے
- [ ] CORS محدود ہے (CORS_ALLOW_ALL_ORIGINS = False)
- [ ] DEBUG = False production میں
- [ ] SECRET_KEY environment variable میں ہے
- [ ] SSL/HTTPS configured
- [ ] Database backups شیڈول ہیں
- [ ] Logs monitored ہیں

---

## 📈 Production Setup

### Gunicorn + Nginx
```bash
# Gunicorn install
pip install gunicorn

# Start
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4

# نیا Dockerfile
FROM python:3.11-slim
...
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Environment Specific
```python
# Production settings
if os.getenv('ENVIRONMENT') == 'production':
    DEBUG = False
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## 🎯 Testing Database

```bash
# Test connection
psql -U skillsphere_user -d skillsphere -h localhost -c "SELECT version();"

# Django test
python manage.py dbshell

# Migration test
python manage.py migrate --plan
python manage.py migrate --dry-run
```

---

## ✨ خلاصہ

✅ **PostgreSQL Setup:**
- Docker Compose fully configured
- Environment variables ready
- Migrations tested
- Security settings added

✅ **Services:**
- PostgreSQL 16
- Redis
- Django
- Celery Worker
- Celery Beat
- Flower

✅ **Ready for:**
- Development
- Production deployment
- Scaling

🚀 **اگلے مرحلہ:** Priority 5 - CORS & Security
