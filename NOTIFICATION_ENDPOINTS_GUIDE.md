# 🔔 Notification Endpoints - راهنمای کامل

## ✅ تکمیل شده

تمام Notification Endpoints آماده و کار می‌کنند!

---

## 📋 API Endpoints

### 1️⃣ **دریافت اعلان‌ها**
```http
GET /api/projects/notifications/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Query Parameters:**
```
?page=1          # صفحه (default: 1)
?limit=20        # تعداد در هر صفحه (default: 20)
```

**پاسخ موفق (200):**
```json
{
  "count": 15,
  "unread_count": 3,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "id": 1,
      "message": "پروژه «My Project» لایک شد",
      "notification_type": "like",
      "is_read": false,
      "sender": {
        "id": 2,
        "email": "user@example.com",
        "name": "احمد"
      },
      "created_at": "2024-07-23T10:30:00Z"
    },
    {
      "id": 2,
      "message": "کامنت جدید روی پروژه شما",
      "notification_type": "chat",
      "is_read": true,
      "sender": {
        "id": 3,
        "email": "another@example.com",
        "name": "علی"
      },
      "created_at": "2024-07-23T09:15:00Z"
    }
  ]
}
```

---

### 2️⃣ **علامت‌گذاری اعلان به عنوان خوانده شده**
```http
POST /api/projects/notifications/{notification_id}/read/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**پاسخ موفق (200):**
```json
{
  "message": "اعلان خوانده شده علامت‌گذاری شد"
}
```

**علامت‌گذاری تمام اعلان‌ها:**
```http
POST /api/projects/notifications/read/
Authorization: Bearer YOUR_JWT_TOKEN
```

---

### 3️⃣ **حذف یک اعلان**
```http
DELETE /api/projects/notifications/{notification_id}/delete/
Authorization: Bearer YOUR_JWT_TOKEN
```

**پاسخ موفق (200):**
```json
{
  "message": "اعلان حذف شد"
}
```

**خطا (404):**
```json
{
  "message": "اعلان یافت نشد"
}
```

---

### 4️⃣ **حذف تمام اعلان‌ها**
```http
DELETE /api/projects/notifications/clear-all/
Authorization: Bearer YOUR_JWT_TOKEN
```

**پاسخ موفق (200):**
```json
{
  "message": "10 اعلان حذف شد"
}
```

---

## 📤 Project Endpoints

### 1️⃣ **آپلود پروژه**
```http
POST /api/projects/upload/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

form-data:
  title: "پروژه من"
  description: "توضیحات پروژه"
  file: (binary file)
```

**پاسخ موفق (201):**
```json
{
  "message": "پروژه با موفقیت آپلود شد",
  "project_id": 1,
  "title": "پروژه من",
  "file_url": "/media/project_files/..."
}
```

---

### 2️⃣ **دریافت فید پروژه‌ها**
```http
GET /api/projects/feed/
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters:**
```
?page=1    # صفحه
?limit=10  # تعداد در هر صفحه
```

**پاسخ (200):**
```json
{
  "count": 50,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "id": 1,
      "title": "پروژه الکترونیکی",
      "description": "یک پروژه خوب",
      "user": {
        "id": 2,
        "email": "creator@example.com",
        "name": "محمد"
      },
      "file_url": "/media/project_files/...",
      "likes_count": 5,
      "comments_count": 2,
      "is_liked_by_user": false,
      "created_at": "2024-07-20T15:30:00Z",
      "download_url": "/api/projects/feed/1/download/"
    }
  ]
}
```

---

### 3️⃣ **لایک/دیس‌لایک پروژه**
```http
POST /api/projects/feed/{project_id}/like/
Authorization: Bearer YOUR_JWT_TOKEN
```

**پاسخ موفق (200):**
```json
{
  "liked": true,
  "total_likes": 6,
  "message": "لایک اضافه شد"
}
```

---

### 4️⃣ **اضافه کردن کامنت**
```http
POST /api/projects/feed/{project_id}/comment/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "content": "یک کامنت عالی!"
}
```

**پاسخ موفق (201):**
```json
{
  "message": "کامنت اضافه شد",
  "comment": {
    "id": 1,
    "content": "یک کامنت عالی!",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "علی"
    },
    "created_at": "2024-07-23T10:45:00Z"
  }
}
```

**دریافت کامنت‌های پروژه:**
```http
GET /api/projects/feed/{project_id}/comment/
Authorization: Bearer YOUR_JWT_TOKEN

?page=1
?limit=20
```

---

### 5️⃣ **دانلود پروژه**
```http
GET /api/projects/feed/{project_id}/download/
Authorization: Bearer YOUR_JWT_TOKEN
```

**پاسخ (200):**
```
File attachment with proper content-type
```

---

## 📊 Analytics Endpoints

### 1️⃣ **تحلیلات سیستم**
```http
GET /api/projects/analytics/
Authorization: Bearer YOUR_JWT_TOKEN
```

**پاسخ (200):**
```json
{
  "summary": {
    "total_projects": 150,
    "user_projects": 5,
    "total_users": 45,
    "total_notifications": 23,
    "unread_notifications": 3,
    "recent_activities_7days": 89
  },
  "popular_projects": [
    {
      "id": 1,
      "title": "پروژه محبوب",
      "likes": 15,
      "user": "creator@example.com"
    }
  ],
  "active_users": [
    {
      "id": 2,
      "email": "active@example.com",
      "activities": 42
    }
  ]
}
```

---

### 2️⃣ **تحلیلات شخصی کاربر**
```http
GET /api/projects/user-analytics/
Authorization: Bearer YOUR_JWT_TOKEN
```

**پاسخ (200):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "احمد"
  },
  "summary": {
    "total_projects": 5,
    "total_likes_received": 23,
    "total_comments_received": 12,
    "total_notifications": 35,
    "recent_activities_7days": 15
  },
  "projects": [
    {
      "id": 1,
      "title": "پروژه اول",
      "likes": 5,
      "comments": 2,
      "created_at": "2024-07-20T10:00:00Z"
    }
  ],
  "notifications_by_type": {
    "like": 20,
    "chat": 12,
    "system": 3
  }
}
```

---

## 🧪 نمونه تست کامل

### مرحله 1: دو کاربر ایجاد کنیں
```bash
# کاربر 1 ایجاد کن
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"pass123","name":"کاربر اول"}'

# کاربر 2 ایجاد کن
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@example.com","password":"pass123","name":"کاربر دوم"}'
```

### مرحله 2: Login کنید
```bash
# کاربر 1 وارد شود
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1@example.com","password":"pass123"}'

# پاسخ:
# {
#   "access": "TOKEN_USER1",
#   "refresh": "REFRESH_TOKEN1",
#   "message": "خوش آمدید!"
# }

# کاربر 2 وارد شود
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user2@example.com","password":"pass123"}'

# TOKEN_USER2 را ذخیره کنید
```

### مرحله 3: کاربر 1 پروژه آپلود کند
```bash
curl -X POST http://localhost:8000/api/projects/upload/ \
  -H "Authorization: Bearer TOKEN_USER1" \
  -F "title=پروژه الکترونیکی" \
  -F "description=پروژه بسیار جالب" \
  -F "file=@/path/to/file.pdf"

# PROJECT_ID را ذخیره کنید (مثال: 1)
```

### مرحله 4: کاربر 2 پروژه را لایک کند
```bash
curl -X POST http://localhost:8000/api/projects/feed/1/like/ \
  -H "Authorization: Bearer TOKEN_USER2"

# پاسخ:
# {
#   "liked": true,
#   "total_likes": 1,
#   "message": "لایک اضافه شد"
# }
```

### مرحله 5: کاربر 1 اعلان را بررسی کند
```bash
curl http://localhost:8000/api/projects/notifications/ \
  -H "Authorization: Bearer TOKEN_USER1"

# پاسخ:
# {
#   "count": 1,
#   "unread_count": 1,
#   "results": [
#     {
#       "id": 1,
#       "message": "پروژه «پروژه الکترونیکی» توسط user2@example.com لایک شد! ❤️",
#       "notification_type": "like",
#       "is_read": false,
#       ...
#     }
#   ]
# }
```

### مرحله 6: اعلان را خوانده شده علامت‌گذاری کنید
```bash
curl -X POST http://localhost:8000/api/projects/notifications/1/read/ \
  -H "Authorization: Bearer TOKEN_USER1"

# پاسخ:
# {
#   "message": "اعلان خوانده شده علامت‌گذاری شد"
# }
```

### مرحله 7: کاربر 2 کامنت اضافه کند
```bash
curl -X POST http://localhost:8000/api/projects/feed/1/comment/ \
  -H "Authorization: Bearer TOKEN_USER2" \
  -H "Content-Type: application/json" \
  -d '{"content":"پروژه عالی‌ای است!"}'

# پاسخ:
# {
#   "message": "کامنت اضافه شد",
#   "comment": {
#     "id": 1,
#     "content": "پروژه عالی‌ای است!",
#     ...
#   }
# }
```

### مرحله 8: تحلیلات را بررسی کنید
```bash
# سیستم تحلیلات
curl http://localhost:8000/api/projects/analytics/ \
  -H "Authorization: Bearer TOKEN_USER1"

# تحلیلات شخصی
curl http://localhost:8000/api/projects/user-analytics/ \
  -H "Authorization: Bearer TOKEN_USER1"
```

---

## 🐛 Error Handling

### خطا: توکن نامعتبر
```
HTTP 401 Unauthorized
{
  "detail": "Invalid token or expired"
}
```

### خطا: اعلان یافت نشد
```
HTTP 404 Not Found
{
  "message": "اعلان یافت نشد"
}
```

### خطا: اعلام موجود نیست
```
HTTP 400 Bad Request
{
  "message": "متن کامنت نمی‌تواند خالی باشد"
}
```

---

## 📝 خلاصه

✅ **تکمیل شدند:**
1. Notification List GET
2. Mark as Read POST
3. Clear Single Notification DELETE
4. Clear All Notifications DELETE
5. Project Feed GET
6. Like Project POST
7. Add Comment POST
8. Get Comments GET
9. Download Project GET
10. System Analytics GET
11. User Analytics GET

🚀 **تمام endpoints آماده برای استفاده هستند!**

---

## 🔄 Integration با Frontend

### مثال React
```javascript
// دریافت اعلان‌ها
const getNotifications = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(
    'http://localhost:8000/api/projects/notifications/?page=1&limit=20',
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.json();
};

// اعلام خوانده شده
const markAsRead = async (notificationId) => {
  const token = localStorage.getItem('token');
  await fetch(
    `http://localhost:8000/api/projects/notifications/${notificationId}/read/`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
};
```

---

## 🎯 بعدی‌ها

### Priority 3️⃣: Celery Tasks
- Email notifications
- Background file processing
- Report generation
