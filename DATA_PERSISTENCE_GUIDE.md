# 📊 Data Persistence Guide

## Problem Fixed
❌ **Before:** After stopping Docker, you had to re-register users  
✅ **After:** Your data is automatically saved between restarts

---

## How It Works

### Database Persistence
Your PostgreSQL database is stored in a **Docker volume** (`postgres_data`)

**Location:** `/var/lib/postgresql/data` (inside container)
**Persisted at:** Docker volumes (host machine)

### Redis Persistence  
Redis cache is stored in a **Docker volume** (`redis_data`)

**Location:** `/data` (inside container)
**Persisted at:** Docker volumes (host machine)

### How Volumes Work
- When you `docker-compose up -d` → Containers start using the volume
- When you `docker-compose down` → Containers stop but volume data **remains**
- When you `docker-compose up -d` again → Containers restart with **old data**

---

## Starting Docker (Ways to Do It)

### Option 1: Simple Command (Keeps Data) ✅ **RECOMMENDED**
```bash
docker-compose up -d
```
✅ Starts containers  
✅ Keeps all database data  
✅ Keeps all user accounts  

### Option 2: Using the Script (Windows)
**Double-click:**
```
START_DOCKER.bat
```
Or in PowerShell:
```powershell
./START_DOCKER.ps1
```

### Option 3: Run in Foreground (For Debugging)
```bash
docker-compose up
```
Shows logs in terminal, press `Ctrl+C` to stop

---

## Stopping Docker (Ways to Do It)

### Option 1: Stop Only (Keeps Data) ✅ **RECOMMENDED FOR QUICK RESTART**
```bash
docker-compose stop
```
✅ Containers are stopped  
✅ **All data is preserved**  
✅ Fast to restart: `docker-compose start`

### Option 2: Stop and Remove Containers (Keeps Data) ✅ **RECOMMENDED FOR CLEANUP**
```bash
docker-compose down
```
✅ Containers removed  
✅ **All data is preserved**  
⏱️ Slower to restart: `docker-compose up -d`

### Option 3: Delete Everything Including Data ❌ **DANGER - USE ONLY IF YOU WANT TO START FRESH**
```bash
docker-compose down -v
```
❌ Containers removed  
❌ **ALL data deleted** (users, projects, etc.)  
⚠️ This is what was happening before!

---

## Common Scenarios

### Scenario 1: Normal Workflow
```bash
# Start Docker
docker-compose up -d

# Use app at http://localhost:5174
# Register once, it saves forever

# Stop Docker later
docker-compose stop

# Next day, restart
docker-compose up -d
# ✅ Your account and projects are still there!
```

### Scenario 2: Restart for Updates
```bash
# Update code files
# Then:
docker-compose restart django

# ✅ Data persists, only app restarts
```

### Scenario 3: Full Cleanup (Start Fresh)
```bash
# Delete everything including data
docker-compose down -v

# Recreate from scratch
docker-compose up -d

# ⚠️ Now you need to register new accounts
```

---

## Checking Data Persistence

### Check PostgreSQL Data
```bash
docker-compose exec postgres psql -U skillsphere_user -d skillsphere -c "SELECT * FROM users_usermodel;"
```

### Check Redis Data
```bash
docker-compose exec redis redis-cli keys '*'
```

### Check Volumes
```bash
docker volume ls | grep skillsphere
```

---

## If Data Gets Lost (Recovery)

### Check if volume still exists
```bash
docker volume ls
```

### If volumes are there but data is gone
```bash
# Check for backup volumes
docker volume inspect skillsphere_postgres_data
```

### Recreate data
```bash
# Option 1: Create backup and restore
docker-compose exec postgres pg_dump -U skillsphere_user skillsphere > backup.sql

# Option 2: Start fresh
docker-compose down -v
docker-compose up -d
```

---

## Configuration Files

### docker-compose.yml
All volumes are defined here:
```yaml
volumes:
  postgres_data:    # Database data
  redis_data:       # Cache data
  elasticsearch_data:  # Search data
```

### Environment Variables (.env)
Database connection is configured:
```
DB_NAME=skillsphere
DB_USER=skillsphere_user
DB_PASSWORD=skillsphere_password
DB_HOST=postgres
DB_PORT=5432
```

---

## Best Practices

✅ **DO:**
- Use `docker-compose stop` when not using the app
- Use `docker-compose up -d` to restart
- Keep `.env` file safe (contains passwords)
- Backup your database regularly

❌ **DON'T:**
- Use `docker-compose down -v` unless you want to delete everything
- Share `.env` file online
- Force kill Docker processes
- Modify volume contents directly

---

## Monitoring

### Check Container Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f django
docker-compose logs -f postgres
```

### Check Resource Usage
```bash
docker stats
```

---

## Troubleshooting

### Q: I accidentally ran `docker-compose down -v` and lost data
**A:** Your data is gone. To prevent this next time:
1. Use `docker-compose stop` or `docker-compose down` (without `-v`)
2. Only use `-v` if you intentionally want to delete

### Q: Database connection fails
**A:** Check if PostgreSQL is running:
```bash
docker-compose logs postgres
```

### Q: Data seems old/outdated
**A:** Verify which version is running:
```bash
docker-compose ps
docker-compose logs django
```

### Q: Migrations failed
**A:** Manually run migrations:
```bash
docker-compose exec django python manage.py migrate
```

---

## Summary

| Command | Containers | Data | Use Case |
|---------|-----------|------|----------|
| `docker-compose up -d` | Start | Keep ✅ | Start services |
| `docker-compose stop` | Stop | Keep ✅ | Temporary pause |
| `docker-compose restart` | Restart | Keep ✅ | Quick restart |
| `docker-compose down` | Stop & Remove | Keep ✅ | Cleanup |
| `docker-compose down -v` | Stop & Remove | Delete ❌ | Full reset |

---

## Next Steps

1. **Always use:** `docker-compose stop` or `docker-compose down` (no `-v`)
2. **Never use:** `docker-compose down -v` unless you know what you're doing
3. **Start now:** `docker-compose up -d` and enjoy persistent data!

✅ **Your data is now safe!**
