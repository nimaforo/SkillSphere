# SkillSphere Quick Start Guide

## 🚀 Getting Started

### 1. Start the System
```bash
cd "C:\Users\nimaf\web project"
docker-compose up -d --build
```

### 2. Verify All Services Running
```bash
docker-compose ps
# Should show 6 containers: postgres, redis, django, celery, beat, flower
```

### 3. Run Migrations (if needed)
```bash
docker-compose exec -T django python manage.py migrate
```

---

## 📝 API Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login (Get JWT Token)
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john@example.com",
    "password": "SecurePass123!"
  }'

# Response: { "access": "eyJhbGc...", "refresh": "eyJhbGc..." }
```

### Get Projects Feed
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/projects/feed/
```

### Upload Project
```bash
curl -X POST http://localhost:8000/api/projects/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@my_project.pdf" \
  -F "title=My Project" \
  -F "description=Project description"
```

### Get Notifications
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/projects/notifications/
```

---

## 🛠️ Useful Commands

### Check Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f django
docker-compose logs -f postgres
docker-compose logs -f celery_worker
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec -T postgres psql -U skillsphere_user -d skillsphere_db

# List tables
\dt

# Query users
SELECT id, username, email FROM users_usermodel;
```

### Django Management
```bash
# Django shell
docker-compose exec -T django python manage.py shell

# Create superuser
docker-compose exec -T django python manage.py createsuperuser

# Check migrations
docker-compose exec -T django python manage.py showmigrations
```

### Celery Tasks
```bash
# View Flower dashboard (Celery monitoring)
# Open: http://localhost:5555

# View Celery logs
docker-compose logs -f celery_worker
```

---

## 📊 Monitoring

| Service | URL | Port |
|---------|-----|------|
| Django API | http://localhost:8000 | 8000 |
| PostgreSQL | localhost | 5432 |
| Redis | localhost | 6379 |
| Flower (Celery) | http://localhost:5555 | 5555 |
| Health Check | http://localhost:8000/health/ | 8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs/swagger/ | 8000 |

---

## ✅ What's Working

- ✅ User registration with email validation
- ✅ JWT-based authentication
- ✅ PostgreSQL database with all migrations
- ✅ File uploads (PDF, ZIP, Images)
- ✅ Project feed with pagination
- ✅ Celery background tasks
- ✅ Redis caching
- ✅ Notifications system
- ✅ WebSocket channels (configured)

---

## ⚠️ Important Notes

1. **Username/Email**: Use email as username for login (not the display username)
2. **JWT Tokens**: Access tokens expire in 24 hours, use refresh token to get new access token
3. **File Upload**: Allowed formats: .pdf, .zip, .rar, .jpg, .jpeg, .png (max 50MB)
4. **CORS**: Configured for localhost:5173 and localhost:5174 (React dev ports)

---

## 🔧 Common Tasks

### Stop All Services
```bash
docker-compose down
```

### Clean Up Everything (including data)
```bash
docker-compose down -v
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build django
```

### View Database Migrations Status
```bash
docker-compose exec -T django python manage.py showmigrations users
```

---

## 📞 Support

For issues, check:
1. `docker-compose logs` for error messages
2. `SYSTEM_STATUS_RESOLVED.md` for detailed troubleshooting
3. Django admin at `/admin/` (if superuser created)
4. API documentation at `/api/docs/swagger/`

---

**Last Updated**: July 23, 2026  
**Status**: ✅ Fully Operational
