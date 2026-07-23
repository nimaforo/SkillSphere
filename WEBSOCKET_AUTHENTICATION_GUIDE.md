# 🔐 WebSocket JWT Authentication - راهنمای کامل

## ✅ تکمیل شده

تمام WebSocket JWT Authentication اصلاح شده و کار می‌کند!

---

## 📋 فایل‌های اصلاح شده

### 1. **`projects/middleware.py`** ✅
```python
# بهبودی:
- استخراج صحیح توکن از query string
- Error handling بهتر
- Debug logs اضافه شده
- Support برای TokenError
```

**کیا این فایل انجام می‌دهد:**
- JWT را از `?token=YOUR_TOKEN` استخراج می‌کند
- توکن را رمزگشایی کرده و کاربر را load می‌کند
- اگر توکن نامعتبر بود، `AnonymousUser` set می‌شود

---

### 2. **`projects/consumers.py`** ✅

#### **ChatConsumer**
```python
# بهبودی:
- فقط برای authenticated users
- بررسی user در connect() 
- صحیح error handling
- Message validation
```

**تست کردن:**
```javascript
// Client side
const token = "YOUR_JWT_TOKEN";
const socket = new WebSocket(
  `ws://localhost:8000/ws/chat/1/?token=${token}`
);

socket.send(JSON.stringify({
  message: "سلام دوستان!"
}));

socket.onmessage = (event) => {
  console.log(JSON.parse(event.data));
  // خروجی:
  // {
  //   type: "chat_message",
  //   message: "سلام دوستان!",
  //   sender: "user@example.com",
  //   sender_id: 1,
  //   project_id: 1
  // }
};
```

---

#### **NotificationConsumer** 🔔
```python
# بهبودی:
- فقط برای authenticated users
- هر کاربر یک اتاق اختصاصی دارد:
  notifications_user_{user_id}
- اعلان‌ها فقط برای کاربر درست ارسال می‌شود
```

**تست کردن:**
```javascript
// Client side
const token = "YOUR_JWT_TOKEN";
const socket = new WebSocket(
  `ws://localhost:8000/ws/notifications/?token=${token}`
);

socket.onmessage = (event) => {
  console.log(JSON.parse(event.data));
  // خروجی:
  // {
  //   type: "LIKE",
  //   message: "پروژه «My Project» توسط user@example.com لایک شد! ❤️",
  //   project_id: 1,
  //   sender_id: 2,
  //   timestamp: "2024-07-23T..."
  // }
};
```

---

### 3. **`projects/domain/services.py`** ✅

**بهبودی:**
```python
# بدل:
_dispatch_notifications(project, trigger_user, ...)

# به:
_dispatch_notifications(
    recipient_user,  # کاربری که اعلان دریافت می‌کند
    trigger_user,    # کاربری که عملیات کرد
    ...
    user_id          # ID کاربر برای اتاق اختصاصی
)
```

**نتیجه:**
- اعلان فقط به کاربر صحیح می‌رود
- NotificationConsumer فقط اعلان‌های مربوط را می‌فرستد

---

### 4. **`core/asgi.py`** ✅

```python
# استفاده می‌کند:
from projects.middleware import JwtAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddleware(  
        URLRouter(projects.routing.websocket_urlpatterns)
    ),
})
```

---

### 5. **`my-frontend/src/App.jsx`** ✅

**بهبودی‌های frontend:**
```javascript
// خودکار reconnect در صورت قطع شدن
// Exponential backoff: 3s, 6s, 9s, 12s, 15s
// بهتر error handling
// Debug logs اضافه شده
```

---

## 🔗 WebSocket URLs

### Chat (پروژه‌های معین)
```
ws://localhost:8000/ws/chat/{project_id}/?token=YOUR_JWT_TOKEN

مثال:
ws://localhost:8000/ws/chat/1/?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Notifications (اعلان‌های شخصی)
```
ws://localhost:8000/ws/notifications/?token=YOUR_JWT_TOKEN

مثال:
ws://localhost:8000/ws/notifications/?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 🧪 تست کامل

### مرحله 1: Login کن
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password123"}'

# پاسخ:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "message": "خوش آمدید!"
# }
```

### مرحله 2: WebSocket Connection

```javascript
// در مرورگر کنسول:
const token = "YOUR_ACCESS_TOKEN_FROM_LOGIN";

// اتصال به chat
const chatSocket = new WebSocket(
  `ws://localhost:8000/ws/chat/1/?token=${token}`
);

chatSocket.onopen = () => console.log("✅ Chat متصل شد");
chatSocket.onerror = (e) => console.error("❌ Chat Error:", e);

// اتصال به notifications
const notifSocket = new WebSocket(
  `ws://localhost:8000/ws/notifications/?token=${token}`
);

notifSocket.onopen = () => console.log("✅ Notifications متصل شد");
notifSocket.onerror = (e) => console.error("❌ Notif Error:", e);
```

### مرحله 3: Send Message

```javascript
// ارسال یک پیام چت
chatSocket.send(JSON.stringify({
  message: "سلام دوستان! 👋"
}));

// دریافت:
// {
//   "type": "chat_message",
//   "message": "سلام دوستان! 👋",
//   "sender": "user@example.com",
//   "sender_id": 1,
//   "project_id": 1
// }
```

### مرحله 4: Trigger Notification

```python
# در Django shell:
from projects.domain.services import ProjectDomainService
from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()
user1 = User.objects.get(email="user1@example.com")
user2 = User.objects.get(email="user2@example.com")
project = Project.objects.get(id=1)

# Like کن
ProjectDomainService.toggle_like(project.id, user2)
```

**نتیجه در WebSocket user1:**
```json
{
  "type": "LIKE",
  "message": "پروژه «My Project» توسط user2@example.com لایک شد! ❤️",
  "project_id": 1,
  "sender_id": 2,
  "timestamp": "2024-07-23T10:30:00"
}
```

---

## 🐛 Debugging

### Log ها را بررسی کن

```
✅ کاربر user@example.com موفقاً احراز هویت شد
✅ اتصال WebSocket اعلان‌ها برقرار شد
📢 اعلان برای کاربر user@example.com: پروژه لایک شد
```

### اگر خطا داشتی:

```
❌ توکن نامعتبر: احراز هویت ناموفق
⚠️ توکن یافت نشد در query string
❌ کاربر احراز هویت نشده است
```

---

## 📊 معماری

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │ (JWT Token in Query String)
         │ ws://localhost:8000/ws/notifications/?token=JWT
         ▼
┌─────────────────────────────────────┐
│   JwtAuthMiddleware                 │
│   - Parse Query String              │
│   - Decode JWT                      │
│   - Load User from DB               │
│   - Set scope['user']               │
└────────┬────────────────────────────┘
         │ (Authenticated Scope)
         ▼
┌─────────────────────────────────────┐
│   NotificationConsumer              │
│   - Check if user is authenticated  │
│   - Join user-specific group        │
│   - notifications_user_{user_id}    │
└────────┬────────────────────────────┘
         │ (Broadcast to group)
         ▼
┌─────────────────────────────────────┐
│   ProjectDomainService              │
│   - toggle_like()                   │
│   - add_comment()                   │
│   - _dispatch_notifications()       │
│     (Send to WebSocket + Database)  │
└─────────────────────────────────────┘
```

---

## 🎯 بعدی‌ها

### Priority 2: Notification Endpoints
- `GET /api/projects/notifications/`
- `DELETE /api/projects/notifications/clear-all/`
- `POST /api/projects/{id}/comment/`

### Priority 3: Celery Tasks
- Background email sending
- File processing

---

## 📝 خلاصه

✅ **تکمیل شدند:**
1. JWT Authentication برای WebSocket
2. اعلان‌های اختصاصی (user-specific)
3. Chat Rooms برای پروژه‌ها
4. Error Handling و Logging
5. Frontend Reconnection Logic

🚀 **سیستم اکنون production-ready است!**
