# SkillSphere - Quick Start Guide

## 🚀 Start the System

```bash
cd "c:\Users\nimaf\web project"
docker-compose up -d --build
```

## 📍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Django API | http://127.0.0.1:8000 | Backend API |
| React Frontend | http://127.0.0.1:5174 | Web Application |
| Flower | http://127.0.0.1:5555 | Task Monitoring |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache/Queue |

## 🔐 Example API Flow

### 1. Register User
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

Response:
```json
{
  "user": {"id": 1, "email": "user@example.com"},
  "message": "Registration successful"
}
```

### 2. Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Get Projects (Authenticated)
```bash
curl http://127.0.0.1:8000/api/projects/feed/ \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Connect to WebSocket (Real-time Notifications)
```javascript
const token = 'YOUR_ACCESS_TOKEN';
const ws = new WebSocket(`ws://127.0.0.1:8000/ws/notifications/?token=${token}`);

ws.onopen = () => {
  console.log('✅ Connected to notifications');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('🔔 Notification:', data.message);
};

ws.onerror = (err) => {
  console.error('❌ WebSocket error:', err);
};
```

## 📊 Available Endpoints

### Projects
- `GET /api/projects/feed/` - List all projects
- `GET /api/projects/analytics/` - Get system analytics
- `POST /api/projects/upload/` - Upload new project
- `POST /api/projects/feed/{id}/like/` - Like project
- `POST /api/projects/feed/{id}/comment/` - Comment on project
- `GET /api/projects/feed/{id}/download/` - Download file

### Notifications
- `GET /api/projects/notifications/` - List notifications
- `DELETE /api/projects/notifications/clear-all/` - Clear all

### User
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `GET /api/user/profile/` - Get user profile

## 🔧 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs django -f
docker-compose logs celery -f
docker-compose logs postgres -f
```

### Apply Migrations
```bash
docker-compose exec -T django python manage.py migrate
```

### Create Admin User
```bash
docker-compose exec -T django python manage.py createsuperuser
```

### Restart Services
```bash
docker-compose restart django
docker-compose restart celery
```

### Stop All Services
```bash
docker-compose down
```

### Clean Up (with data wipe)
```bash
docker-compose down -v
```

## 🧪 Testing WebSocket

### Using WebSocket Test Client (Node.js)
```javascript
const WebSocket = require('ws');

async function testWebSocket() {
  // First login to get token
  const loginRes = await fetch('http://127.0.0.1:8000/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'user@example.com',
      password: 'SecurePass123!'
    })
  });
  
  const { access } = await loginRes.json();
  
  // Connect to WebSocket
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/notifications/?token=${access}`);
  
  ws.on('open', () => {
    console.log('✅ Connected');
  });
  
  ws.on('message', (data) => {
    console.log('📨 Received:', JSON.parse(data));
  });
}

testWebSocket();
```

## 📝 Environment Variables

### .env (Development)
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=skillsphere_db
DB_USER=skillsphere_user
DB_PASSWORD=skillsphere_password
DB_HOST=postgres
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=django-db

CORS_ALLOWED_ORIGINS=http://127.0.0.1:5174

SECRET_KEY=your-secret-key-here
```

## 🐛 Troubleshooting

### Django not starting
```bash
docker-compose logs django | tail -50
docker-compose restart django
```

### Celery tasks not running
```bash
docker-compose logs celery | tail -50
docker-compose restart celery
docker-compose restart celery_beat
```

### Database connection error
```bash
docker-compose exec -T postgres psql -U skillsphere_user -d skillsphere_db
```

### React can't reach API
- Check if Django is running: `docker-compose ps`
- Verify CORS settings in `core/settings.py`
- Check Accept headers in fetch requests

### WebSocket connection fails
- Verify token is valid (decode at jwt.io)
- Check if Django WebSocket server is running
- Review WebSocket logs: `docker-compose logs django -f`

## 📈 Monitoring

### Celery Tasks
Visit http://127.0.0.1:5555 to see:
- Active tasks
- Completed tasks
- Failed tasks
- Task history
- Worker status

### Database
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db

# View tables
\dt

# Exit
\q
```

## 🎯 Key Ports

- **8000** - Django ASGI/Daphne server
- **5174** - React Vite development server
- **5555** - Flower (Celery monitoring)
- **5432** - PostgreSQL database
- **6379** - Redis cache

## 📚 Documentation

- Django: https://docs.djangoproject.com/
- Django Channels: https://channels.readthedocs.io/
- Celery: https://docs.celeryproject.org/
- React: https://react.dev
- WebSocket: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

## 🆘 Need Help?

1. Check logs: `docker-compose logs SERVICE_NAME -f`
2. Verify migrations: `docker-compose exec -T django python manage.py showmigrations`
3. Test endpoint: `curl http://127.0.0.1:8000/health/`
4. Review settings: `docker-compose exec -T django python manage.py diffsettings`

---

**System Status**: ✅ All Services Running
**Last Updated**: July 23, 2026
