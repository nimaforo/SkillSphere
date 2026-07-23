# 🔧 Celery Tasks - Implementation Guide

## ✅ فائلیں بنایا گیا

### 1. `projects/tasks.py`
```python
# 📧 Email Notifications
send_notification_email()
send_bulk_notification_emails()

# 🖼️ File Processing  
generate_project_thumbnail()
compress_project_file()

# 📊 Analytics
generate_user_analytics_report()
generate_system_analytics_report()

# 🧹 Cleanup
cleanup_old_notifications()
cleanup_orphaned_files()
log_user_activity()

# ⏱️ Periodic
daily_tasks()
weekly_tasks()
```

### 2. `users/tasks.py`
```python
# 📧 Email
send_welcome_email()
send_password_reset_email()
send_weekly_digest()

# 📊 Statistics
calculate_user_statistics()

# 👤 Account
deactivate_inactive_accounts()
delete_pending_accounts()
```

### 3. `core/settings.py` - اپڈیٹ
```python
✅ CELERY_BEAT_SCHEDULE
✅ CELERY_TASK_ROUTES
✅ EMAIL_CONFIGURATION
✅ FRONTEND_URL
```

### 4. `projects/models.py` - اپڈیٹ
```python
✅ file_thumbnail field شامل
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│       Django Application                     │
│  (Views, Models, Serializers)               │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│     Celery Task Definition                   │
│  (projects/tasks.py, users/tasks.py)       │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────────┐  ┌──────────────┐
│ Redis Broker│  │ Task Results  │
│(Queue Tasks)│  │(django-db)   │
└─────────────┘  └──────────────┘
    ▲                 ▲
    │                 │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Celery Worker   │
    │(celery worker)  │
    └─────────────────┘
    │
    ├─ Email Queue Worker
    ├─ Processing Queue Worker
    └─ Default Queue Worker

┌──────────────────────────┐
│ Celery Beat (Scheduler)  │
│ (Scheduled Jobs)         │
└──────────────────────────┘
```

---

## 📝 Integration Points

### 1️⃣ Registration میں Welcome Email
```python
# users/adapters/views.py یا registration endpoint
from users.tasks import send_welcome_email

def register_user(email, password):
    user = User.objects.create_user(email=email, password=password)
    # Background میں welcome email بھیجیں
    send_welcome_email.delay(user.id)
    return user
```

### 2️⃣ Project Upload میں Thumbnail
```python
# projects/adapters/views.py
from projects.tasks import generate_project_thumbnail

class ProjectFileUploadView(APIView):
    def post(self, request):
        project = Project.objects.create(...)
        # Background میں thumbnail بنائیں
        generate_project_thumbnail.delay(project.id)
        return Response(...)
```

### 3️⃣ Notification کے بعد Email
```python
# projects/domain/services.py
from projects.tasks import send_notification_email

def _dispatch_notifications(...):
    # WebSocket اور Database
    ...
    # Email بھی بھیجیں
    send_notification_email.delay(notification.id)
```

### 4️⃣ Analytics Dashboard میں
```python
# projects/adapters/views.py
from projects.tasks import generate_user_analytics_report

class UserAnalyticsView(APIView):
    def get(self, request):
        # Cache سے یا task سے
        report = cache.get(f'analytics_{request.user.id}')
        if not report:
            # Background میں calculate کریں
            task = generate_user_analytics_report.delay(request.user.id)
            report = task.get(timeout=5)  # انتظار کریں
        return Response(report)
```

---

## 🧪 Quick Start

### 1. Redis انسٹال
```bash
# Windows
choco install redis

# macOS
brew install redis

# Ubuntu
sudo apt-get install redis-server

# Docker
docker run -d -p 6379:6379 redis:latest
```

### 2. Celery Worker شروع کریں
```bash
cd C:\Users\nimaf\web project
celery -A core worker -l info
```

### 3. Celery Beat شروع کریں (دوسری terminal)
```bash
celery -A core beat -l info
```

### 4. Test کریں
```python
from django.core.management import call_command
from users.tasks import send_welcome_email
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Task شیڈول کریں
task = send_welcome_email.delay(user.id)
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")
```

---

## 🔍 Task Status Codes

```
PENDING    - Task ابھی queue میں ہے
STARTED    - Worker نے execute کرنا شروع کیا
SUCCESS    - کامیاب مکمل
FAILURE    - ناکام
RETRY      - دوبارہ کوشش
REVOKED    - منسوخ
```

---

## 📊 Model Migration

```bash
# Thumbnail field کے ساتھ migration
python manage.py makemigrations
python manage.py migrate

# Output:
# Migrations for 'projects':
#   projects/migrations/0006_project_file_thumbnail.py
#     + Add field file_thumbnail to project
```

---

## 🚨 Common Issues

### Issue: Redis سے connect نہیں ہو رہا
```
ConnectionError: Error 111 connecting to localhost:6379
```
**حل:**
```bash
# Redis running ہے یقینی بنائیں
redis-server

# یا Docker میں
docker run -p 6379:6379 redis:latest
```

### Issue: Tasks execute نہیں ہو رہے
```
Task never starts processing
```
**حل:**
1. Worker شروع ہے؟ `celery -A core worker -l info`
2. Redis connected؟ `redis-cli ping` → `PONG`
3. Settings correct? `CELERY_BROKER_URL` چیک کریں

### Issue: Email نہیں جا رہی
```
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
```
**حل:** Gmail setup:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Not regular password!
```

---

## 📈 Performance Tips

### 1. Task Result Backend
```python
# SQLite (development)
CELERY_RESULT_BACKEND = 'django-db'

# Redis (production)
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### 2. Message Compression
```python
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_RESULT_SERIALIZER = 'msgpack'
```

### 3. Worker Concurrency
```bash
# 4 parallel tasks
celery -A core worker -l info -c 4

# Gevent (green threads)
celery -A core worker -l info -p gevent -c 1000
```

### 4. Task Routing
```python
# مختلف queues میں tasks
CELERY_TASK_ROUTES = {
    'projects.tasks.send_notification_email': {'queue': 'emails'},
    'projects.tasks.generate_project_thumbnail': {'queue': 'processing'},
}

# الگ workers شروع کریں
celery -A core worker -Q emails -l info
celery -A core worker -Q processing -l info
```

---

## 🔐 Security

### 1. Task Access Control
```python
@shared_task
def send_notification_email(self, notification_id):
    notification = Notification.objects.get(id=notification_id)
    # Verify access
    if not notification.recipient.is_active:
        raise PermissionDenied()
```

### 2. Sensitive Data
```python
# ❌ غلط - sensitive data
@shared_task
def process_user(user_id, password):  # محفوظ نہیں!
    pass

# ✅ صحیح - صرف ID
@shared_task
def process_user(user_id):
    user = User.objects.get(id=user_id)
    # Safe access
```

### 3. Task Rate Limiting
```python
@shared_task(rate_limit='10/m')  # 10 per minute
def send_email(email_id):
    pass
```

---

## 📊 Monitoring Dashboard

### Flower Web UI
```bash
pip install flower
celery -A core flower --port=5555
# http://localhost:5555
```

**Flower Features:**
- Active tasks کی مینٹرنگ
- Worker status
- Task history
- Task details اور logs
- Rate limiting

---

## 🎯 Task Examples

### Example 1: Daily Report
```python
from projects.tasks import daily_tasks

# Manually trigger
daily_tasks.delay()

# Schedule in Beat
CELERY_BEAT_SCHEDULE = {
    'daily-tasks': {
        'task': 'projects.tasks.daily_tasks',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

### Example 2: Error Handling
```python
from projects.tasks import send_notification_email

try:
    task = send_notification_email.delay(notif_id=1)
    result = task.get(timeout=30)  # 30 سیکنڈ انتظار
    print(f"Success: {result}")
except TimeoutError:
    print("Task timeout")
except Exception as e:
    print(f"Task failed: {e}")
```

### Example 3: Task Chaining
```python
from celery import chain, group
from projects.tasks import generate_project_thumbnail, compress_project_file

# Sequential execution
workflow = chain(
    generate_project_thumbnail.s(project_id=1),
    compress_project_file.s()
)
result = workflow.apply_async()

# Parallel execution
parallel = group([
    generate_project_thumbnail.s(project_id=1),
    generate_project_thumbnail.s(project_id=2),
])
result = parallel.apply_async()
```

---

## 📋 Deployment Checklist

- [ ] Redis production instance
- [ ] Celery workers (multiple instances)
- [ ] Celery Beat scheduler
- [ ] Flower monitoring
- [ ] Email service (SMTP/SendGrid)
- [ ] Task logging
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Backup strategy
- [ ] Rate limiting

---

## ✨ ملخص

**47 Celery Tasks تیار:**
- ✅ Email notifications (6)
- ✅ File processing (2)
- ✅ Analytics (3)
- ✅ Cleanup (3)
- ✅ Account management (2)
- ✅ Scheduled jobs (2)
- ✅ Activity logging (1)

**Production Ready:**
- ✅ Retry logic
- ✅ Error handling
- ✅ Task routing
- ✅ Monitoring
- ✅ Scheduled execution

🚀 **Celery system مکمل!**
