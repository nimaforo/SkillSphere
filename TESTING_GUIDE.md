# 🧪 SkillSphere Testing Guide

## Status: ✅ READY FOR TESTING

All services running and frontend connected. Follow this guide to verify everything works.

---

## 🚀 Access Points

### Frontend
- **URL:** http://localhost:5174/
- **Status:** Vite dev server running
- **Port:** 5174 (if 5173 in use)

### Backend
- **API URL:** http://localhost:8000/
- **Health Check:** http://localhost:8000/health/
- **Admin Panel:** http://localhost:8000/admin/

### Documentation
- **Swagger API Docs:** http://localhost:8000/api/docs/swagger/
- **ReDoc Docs:** http://localhost:8000/api/docs/redoc/

### Monitoring
- **Celery Monitor (Flower):** http://localhost:5555/
- **Database:** PostgreSQL @ localhost:5432
- **Cache:** Redis @ localhost:6379

---

## 📋 Testing Checklist

### Phase 1: Backend Health Checks

#### 1.1 Health Endpoint
```bash
curl http://localhost:8000/health/
```

Expected Response:
```json
{
  "status": "healthy",
  "service": "skillsphere-api",
  "version": "1.0.0"
}
```

#### 1.2 Admin Access
- URL: http://localhost:8000/admin/
- **Username:** admin
- **Password:** admin123456
- **Expected:** Django admin dashboard loads

#### 1.3 Database Status
```bash
docker-compose exec postgres psql -U skillsphere_user -d skillsphere_db -c "SELECT COUNT(*) FROM projects_project;"
```

Expected: Shows project count (0 if empty)

#### 1.4 Redis Status
```bash
docker-compose exec redis redis-cli ping
```

Expected Response: `PONG`

#### 1.5 Celery Status
```bash
docker-compose exec celery_worker celery -A core inspect active
```

Expected: Shows active workers

---

### Phase 2: Frontend Testing

#### 2.1 Frontend Loads
- Open: http://localhost:5174/
- Expected: Auth page or Dashboard loads
- Check Console: Should have debug logs (not errors)

#### 2.2 Check Console Logs
Open Browser DevTools → Console
Should see messages like:
```
✅ اعلان‌ها دریافت شدند: ...
✅ Projects fetched: ...
✅ Analytics fetched: ...
```

#### 2.3 Network Tab
Open Browser DevTools → Network
Should see requests to:
- `http://localhost:8000/api/projects/feed/`
- `http://localhost:8000/api/projects/notifications/`
- `http://localhost:8000/health/`

Status should be 200 (OK)

---

### Phase 3: Authentication Flow

#### 3.1 Register User
1. Go to http://localhost:5174/
2. Click "Register" (if available)
3. Fill form:
   ```
   Email: testuser@example.com
   Username: testuser
   Password: TestPass123!
   ```
4. Click Submit
5. Expected: Success message or redirect to login

#### 3.2 Login User
1. Enter credentials:
   ```
   Email: testuser@example.com
   Password: TestPass123!
   ```
2. Click Login
3. Expected: Redirected to Dashboard
4. Check Console: JWT token should be in localStorage

#### 3.3 Verify JWT Token
Browser Console:
```javascript
localStorage.getItem('token')
// Should output: eyJ... (long JWT string)
```

---

### Phase 4: API Endpoints Testing

#### 4.1 Test Projects Feed (No Auth Required)
```bash
curl http://localhost:8000/api/projects/feed/
```

Expected Response:
```json
{
  "count": 0,
  "page": 1,
  "limit": 10,
  "results": []
}
```

#### 4.2 Test Health Endpoint
```bash
curl http://localhost:8000/health/
```

#### 4.3 Test With Authentication
```bash
TOKEN="your_jwt_token_here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/projects/notifications/
```

---

### Phase 5: Frontend Features

#### 5.1 Dashboard Page
- Expected: System statistics displayed
- Shows: Total users, projects, comments
- Falls back gracefully if API empty

#### 5.2 Project Feed
- Expected: List of projects (empty initially)
- Can like projects (if logged in)
- Can add comments (if logged in)

#### 5.3 Notifications
- Expected: Notification bell icon in header
- Shows notification count
- Can mark as read/delete

#### 5.4 Notifications Dropdown
- Click bell icon
- Should show notifications (empty initially)
- Can clear all notifications

---

### Phase 6: WebSocket Testing

#### 6.1 WebSocket Connection
Browser Console (after login):
```
✅ اتصال WebSocket اعلان‌ها برقرار شد
🔌 اتصال WebSocket قطع شد (if it disconnects)
```

#### 6.2 Real-time Notifications
Expected behavior:
- WebSocket connects after login
- Receives notification messages
- Updates UI in real-time

#### 6.3 WebSocket with Token
Check that WebSocket connects with token:
```
ws://127.0.0.1:8000/ws/notifications/?token=JWT_TOKEN
```

---

### Phase 7: Error Handling

#### 7.1 Test Invalid Token
Browser Console:
```javascript
localStorage.setItem('token', 'invalid-token');
// Reload page - should show error or redirect
```

#### 7.2 Test Expired Token
Wait for token to expire (if configured) then:
- Refresh page
- Should redirect to login
- Should not crash

#### 7.3 API Error Handling
- If backend is down: should show error message
- If network fails: should retry
- Should not crash app

---

### Phase 8: Celery Background Tasks

#### 8.1 Monitor Flower
- Open: http://localhost:5555
- Expected: Flower dashboard loads
- Shows: Workers, tasks, scheduling info

#### 8.2 Check Active Tasks
```bash
docker-compose exec celery_worker celery -A core inspect active
```

#### 8.3 Test Email Tasks (if configured)
Send test email task and verify:
- Task appears in Flower
- Task completes successfully
- Email received (if SMTP configured)

---

### Phase 9: Security Testing

#### 9.1 CORS Headers
```bash
curl -i -X OPTIONS http://localhost:8000/api/projects/feed/
```

Should include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

#### 9.2 HTTPS/Security Headers (Production)
```bash
curl -i https://api.skillsphere.com/
```

Should include:
```
Strict-Transport-Security: max-age=31536000
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

#### 9.3 Rate Limiting
```bash
# Send 150 requests quickly (should be rate limited after ~100)
for i in {1..150}; do curl http://localhost:8000/health/; done
```

Should eventually get 429 (Too Many Requests)

---

## 🐛 Debugging Tips

### Check Django Logs
```bash
docker-compose logs django -f
```

Look for:
- ✅ `Watching for file changes` (ready)
- ❌ Syntax errors or exceptions
- ⚠️ Warnings about configuration

### Check Celery Logs
```bash
docker-compose logs celery_worker -f
```

Look for:
- ✅ `Connected to amqp://` (connected to Redis)
- ✅ Task messages
- ❌ Connection errors

### Check Frontend Console
Open Browser DevTools → Console

Should see:
- ✅ Successful API calls
- ✅ WebSocket connections
- ❌ CORS errors → check backend CORS config
- ❌ 404 errors → check endpoints

### Test Specific Endpoint
```bash
curl -v http://localhost:8000/api/projects/feed/
```

The `-v` flag shows all headers and response details

---

## ✅ Passing Criteria

### Backend ✅
- [ ] Health check returns 200
- [ ] Admin panel accessible
- [ ] All endpoints respond (no 500 errors)
- [ ] Celery workers active
- [ ] Database connected
- [ ] Redis connected

### Frontend ✅
- [ ] Page loads without errors
- [ ] Can register/login
- [ ] Can view dashboard
- [ ] Can view projects
- [ ] Can see notifications
- [ ] No console errors
- [ ] API calls succeed

### Integration ✅
- [ ] Frontend connects to backend
- [ ] WebSocket connects after login
- [ ] Real-time updates working
- [ ] Error handling graceful
- [ ] All forms work

### Security ✅
- [ ] JWT tokens valid
- [ ] CORS working
- [ ] Authentication required
- [ ] Rate limiting active
- [ ] Errors don't expose stack traces

---

## 🚀 If All Tests Pass

Congratulations! You can now:

1. **Create Test Data**
   - Use admin to create projects
   - Create test users
   - Generate notifications

2. **Test Full Flow**
   - User registers → logs in → sees projects → real-time updates

3. **Performance Testing**
   - Load test with multiple users
   - Monitor resource usage
   - Check response times

4. **Move to Production**
   - Configure `.env.production`
   - Set up SSL
   - Deploy to cloud

---

## ❌ If Tests Fail

### Issue: Frontend doesn't load
- [ ] Check if dev server is running: `npm run dev`
- [ ] Check port 5174 is accessible
- [ ] Check console for errors
- [ ] Check network tab for failed requests

### Issue: API returns 500
- [ ] Check Django logs: `docker-compose logs django`
- [ ] Check if migrations ran: `docker-compose exec django python manage.py migrate`
- [ ] Check database connection

### Issue: WebSocket not connecting
- [ ] Check if token is valid
- [ ] Check browser console for WebSocket errors
- [ ] Verify middleware is loaded

### Issue: CORS errors
- [ ] Check `CORS_ALLOWED_ORIGINS` in settings.py
- [ ] Add frontend URL if not in whitelist
- [ ] Restart Django: `docker-compose restart django`

---

## 📊 Test Results Template

```
Date: ___________
Tester: ___________

Backend Health: _____ / 6 passed
Frontend Features: _____ / 4 passed
Integration: _____ / 4 passed
Security: _____ / 4 passed

Issues Found:
1. _______________________
2. _______________________

Overall Status: [ ] PASS [ ] FAIL [ ] CONDITIONAL
```

---

## 📞 Quick Reference

| What | Command |
|------|---------|
| View logs | `docker-compose logs -f` |
| Restart Django | `docker-compose restart django` |
| Restart all | `docker-compose restart` |
| Stop all | `docker-compose down` |
| Start all | `docker-compose up -d` |
| Django shell | `docker-compose exec django python manage.py shell` |
| Run migrations | `docker-compose exec django python manage.py migrate` |
| Create user | `docker-compose exec django python manage.py createsuperuser` |

---

**Last Updated:** July 23, 2026  
**Status:** Ready for Testing  
**Next:** QA Verification
