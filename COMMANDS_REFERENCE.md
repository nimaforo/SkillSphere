# SkillSphere - Commands Reference Guide

## 🚀 Startup & Shutdown

### Start All Services
```bash
cd "c:\Users\nimaf\web project"
docker-compose up -d --build
```

### Stop All Services
```bash
docker-compose down
```

### Stop and Delete Everything (Clean Slate)
```bash
docker-compose down -v
docker system prune -f
```

### Restart Specific Service
```bash
docker-compose restart django
docker-compose restart celery
docker-compose restart postgres
docker-compose restart redis
```

---

## 🔧 Database Operations

### Apply Migrations
```bash
docker-compose exec -T django python manage.py migrate
```

### Check Migration Status
```bash
docker-compose exec -T django python manage.py showmigrations
docker-compose exec -T django python manage.py showmigrations users
docker-compose exec -T django python manage.py showmigrations projects
```

### Create Superuser
```bash
docker-compose exec django python manage.py createsuperuser
```

### Connect to PostgreSQL CLI
```bash
docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db
```

### Run Django Shell
```bash
docker-compose exec django python manage.py shell
```

### Create Test Data
```bash
docker-compose exec django python manage.py shell
>>> from users.models import CustomUser
>>> user = CustomUser.objects.create_user(email='test@test.com', password='test123')
>>> user.save()
>>> exit()
```

---

## 📊 Logging & Monitoring

### View All Logs (Real-time)
```bash
docker-compose logs -f
```

### View Django Logs
```bash
docker-compose logs django -f
```

### View Celery Logs
```bash
docker-compose logs celery -f
```

### View PostgreSQL Logs
```bash
docker-compose logs postgres -f
```

### View Redis Logs
```bash
docker-compose logs redis -f
```

### View Last N Lines
```bash
docker-compose logs django --tail=50
docker-compose logs celery --tail=100
```

### Check Service Status
```bash
docker-compose ps
```

---

## 🧪 Testing & Validation

### Test Health Endpoint
```bash
curl http://127.0.0.1:8000/health/
```

### Test User Registration
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Test User Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

### Test Projects Feed (Requires Token)
```bash
export TOKEN="your_jwt_token_here"
curl http://127.0.0.1:8000/api/projects/feed/ \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Analytics (Requires Token)
```bash
curl http://127.0.0.1:8000/api/projects/analytics/ \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Notifications (Requires Token)
```bash
curl http://127.0.0.1:8000/api/projects/notifications/ \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎵 Celery & Task Management

### View Celery Tasks (via Flower)
- Open: http://127.0.0.1:5555
- See active, completed, failed tasks
- Monitor worker performance
- View task history

### Run Specific Celery Task
```bash
docker-compose exec django python manage.py shell
>>> from projects.tasks import send_notification_email
>>> send_notification_email.delay('user@example.com', 'Test Subject', 'Test Message')
```

### Check Celery Worker Status
```bash
docker-compose exec celery celery -A core inspect active
docker-compose exec celery celery -A core inspect registered
```

### Purge All Celery Tasks
```bash
docker-compose exec celery celery -A core purge
```

---

## 📁 File Operations

### View Django Files
```bash
docker-compose exec django ls -la /app
```

### View Database Files
```bash
docker-compose exec postgres ls -la /var/lib/postgresql/data
```

### Copy File from Container
```bash
docker cp skillsphere_django:/app/manage.py ./
```

### Copy File to Container
```bash
docker cp ./requirements.txt skillsphere_django:/app/
```

---

## 🔍 Debugging

### Access Django Container Shell
```bash
docker-compose exec django bash
```

### Access PostgreSQL Container Shell
```bash
docker-compose exec postgres bash
```

### Access Redis Container Shell
```bash
docker-compose exec redis bash
```

### Check Python Packages
```bash
docker-compose exec django pip list
```

### Check Database Tables
```bash
docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db -c "\dt"
```

### Check User Existence
```bash
docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db -c "SELECT id, email FROM users_customuser;"
```

---

## 🚨 Troubleshooting Commands

### Check Port Availability
```bash
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :6379
netstat -ano | findstr :5555
```

### Kill Process on Port (if needed)
```bash
taskkill /PID <PID> /F
```

### Rebuild Images (Force)
```bash
docker-compose build --no-cache
docker-compose up -d --build
```

### Check Disk Usage
```bash
docker system df
docker image ls
docker container ls -a
```

### Full System Cleanup
```bash
docker-compose down -v
docker system prune -af --volumes
```

---

## 📈 Performance Commands

### Monitor Real-Time Stats
```bash
docker stats
```

### Check Memory/CPU Usage
```bash
docker-compose exec django ps aux
docker-compose exec postgres ps aux
```

### Check Network
```bash
docker network ls
docker network inspect webproject_skillsphere_network
```

---

## 🔐 Security Commands

### Generate New Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Change Django Admin Password
```bash
docker-compose exec django python manage.py changepassword admin
```

### Verify SSL/TLS Headers
```bash
curl -I http://127.0.0.1:8000/health/
```

---

## 📦 Dependency Commands

### Add New Python Package
```bash
# 1. Add to requirements.txt
# 2. Rebuild container
docker-compose build --no-cache django
docker-compose up -d
```

### Update All Packages
```bash
docker-compose exec django pip install --upgrade -r requirements.txt
```

---

## 🎯 Common Workflows

### Start Fresh Development Session
```bash
# 1. Stop all services
docker-compose down

# 2. Start fresh with migrations
docker-compose up -d --build
docker-compose exec -T django python manage.py migrate

# 3. Verify health
curl http://127.0.0.1:8000/health/
```

### Debug API Issue
```bash
# 1. Check Django logs
docker-compose logs django --tail=100

# 2. Check if migrations are applied
docker-compose exec -T django python manage.py showmigrations

# 3. Test endpoint directly
curl http://127.0.0.1:8000/health/

# 4. Check database connection
docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db -c "SELECT 1;"
```

### Deploy Code Changes
```bash
# 1. Make code changes locally
# 2. Stop containers
docker-compose down

# 3. Rebuild and restart
docker-compose up -d --build

# 4. Apply any new migrations
docker-compose exec -T django python manage.py migrate

# 5. Restart Celery
docker-compose restart celery celery_beat

# 6. Verify
docker-compose ps
```

### Reset Database (Lose All Data)
```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d --build
docker-compose exec -T django python manage.py migrate
```

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start System | `docker-compose up -d --build` |
| Stop System | `docker-compose down` |
| View Logs | `docker-compose logs -f` |
| Apply Migrations | `docker-compose exec -T django python manage.py migrate` |
| Run Django Shell | `docker-compose exec django python manage.py shell` |
| Check Health | `curl http://127.0.0.1:8000/health/` |
| View Celery Tasks | http://127.0.0.1:5555 |
| Connect PostgreSQL | `docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db` |
| View Containers | `docker-compose ps` |
| Rebuild Images | `docker-compose build --no-cache` |
| Full Cleanup | `docker-compose down -v && docker system prune -af --volumes` |

---

## 🌐 Service URLs

| Service | URL |
|---------|-----|
| Django API | http://127.0.0.1:8000 |
| React Frontend | http://127.0.0.1:5174 |
| Flower (Tasks) | http://127.0.0.1:5555 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| Health Check | http://127.0.0.1:8000/health/ |

---

**Last Updated**: July 23, 2026
