# 🛡️ SkillSphere Security Guide

## Overview
Complete security implementation guide for SkillSphere platform, covering authentication, authorization, data protection, and operational security.

---

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [CORS & Security Headers](#cors--security-headers)
3. [Input Validation & Data Sanitization](#input-validation--data-sanitization)
4. [Rate Limiting & DDoS Protection](#rate-limiting--ddos-protection)
5. [Logging & Audit Trail](#logging--audit-trail)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [API Security](#api-security)
8. [WebSocket Security](#websocket-security)
9. [File Upload Security](#file-upload-security)
10. [Database Security](#database-security)
11. [Production Deployment](#production-deployment)

---

## Authentication & Authorization

### JWT Configuration

```python
# core/settings.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'JTI_CLAIM': 'jti',
}
```

### WebSocket JWT Authentication

```python
# projects/middleware.py
from urllib.parse import parse_qs
from jwt import decode, InvalidTokenError

class JwtAuthMiddleware:
    """
    WebSocket JWT Authentication Middleware
    Validates JWT token from WebSocket query string
    """
    
    def __init__(self, inner):
        self.inner = inner
    
    def __call__(self, scope):
        headers = dict(scope.get("headers", []))
        
        # Parse JWT from query string
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]
        
        if token:
            try:
                payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                scope['user_id'] = payload['user_id']
            except InvalidTokenError:
                scope['user_id'] = None
        else:
            scope['user_id'] = None
        
        return self.inner(scope)
```

### Permission Classes

```python
# projects/permissions.py
from rest_framework import permissions

class IsProjectOwner(permissions.BasePermission):
    """
    Only project owner can modify
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsCommentAuthor(permissions.BasePermission):
    """
    Only comment author can delete
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
```

---

## CORS & Security Headers

### CORS Configuration

```python
# core/settings.py
CORS_ALLOWED_ORIGINS = [
    "https://skillsphere.com",
    "https://www.skillsphere.com",
    "https://app.skillsphere.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Security Headers

```python
# core/settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'", "https:"),
    'script-src': ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"),
    'style-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'", "https:"),
    'connect-src': ("'self'", "https:", "wss:"),
}

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# X-Frame-Options
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

---

## Input Validation & Data Sanitization

### Using Validators

```python
# projects/adapters/serializers.py
from core.validators import (
    validate_email, 
    validate_text_input, 
    validate_file_size,
    validate_file_extension
)

class ProjectCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=5000)
    file = serializers.FileField()
    
    def validate_title(self, value):
        validate_text_input(value, min_length=3, max_length=200)
        return value
    
    def validate_description(self, value):
        validate_text_input(value, min_length=10, max_length=5000)
        return value
    
    def validate_file(self, value):
        validate_file_size(value, max_size_mb=50)
        validate_file_extension(value.name, ['pdf', 'zip', 'txt'])
        return value
```

### XSS Prevention

```python
# core/security.py
def sanitize_html(html_content):
    """Sanitize HTML content"""
    import bleach
    
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)
```

### SQL Injection Prevention

```python
# Always use Django ORM!
# ✅ GOOD
Project.objects.filter(title__icontains=search_query)

# ❌ BAD - Never do this!
Project.objects.raw(f"SELECT * FROM projects WHERE title LIKE '%{search_query}%'")
```

---

## Rate Limiting & DDoS Protection

### Per-Endpoint Rate Limiting

```python
# core/settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',           # Anonymous users
        'user': '1000/hour',          # Authenticated users
        'uploads': '5/hour',          # File uploads
        'notifications': '50/hour',   # Notifications
    }
}
```

### Custom Throttle Classes

```python
# core/throttles.py
from rest_framework.throttling import UserRateThrottle

class UploadThrottle(UserRateThrottle):
    scope = 'uploads'

class AuthThrottle(UserRateThrottle):
    scope = 'auth'
```

### Nginx-Level Rate Limiting

```nginx
# nginx.conf
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;

location /api/ {
    limit_req zone=api burst=30 nodelay;
    proxy_pass http://django_backend;
}
```

---

## Logging & Audit Trail

### Audit Logging Implementation

```python
# core/security.py
class AuditLogger:
    """Audit logging for security events"""
    
    @staticmethod
    def log_login(user, ip_address=None):
        logger.info(
            f'User {user.email} logged in from {ip_address}',
            extra={'user_id': user.id, 'ip': ip_address}
        )
    
    @staticmethod
    def log_password_change(user, ip_address=None):
        logger.info(
            f'User {user.email} changed password',
            extra={'user_id': user.id, 'ip': ip_address}
        )
```

### Security Logging Configuration

```python
# core/settings.py
LOGGING = {
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024 * 1024 * 15,
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
        },
    },
}
```

---

## SSL/TLS Configuration

### HTTPS Enforcement

```python
# core/settings.py
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Certificate Management

See **SSL_SETUP_GUIDE.md** for detailed SSL/TLS setup instructions.

---

## API Security

### CSRF Protection

```python
# core/settings.py
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://skillsphere.com',
    'https://www.skillsphere.com',
]
```

### Session Security

```python
# core/settings.py
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### API Versioning

```python
# core/urls.py
from rest_framework.routers import DefaultRouter
from projects.adapters.views import ProjectViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

---

## WebSocket Security

### JWT Validation in WebSocket

```python
# projects/consumers.py
from channels.db import database_sync_to_async
from core.exceptions import UserNotAuthenticatedException

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope.get('user_id')
        
        if not user_id:
            await self.close()
            return
        
        self.user_id = user_id
        await self.accept()
```

### Per-User Notification Groups

```python
# projects/consumers.py
async def connect(self):
    self.user_id = self.scope['user_id']
    self.notification_group = f'notifications_user_{self.user_id}'
    
    await self.channel_layer.group_add(
        self.notification_group,
        self.channel_name
    )
```

---

## File Upload Security

### File Validation

```python
# core/validators.py
def validate_file_size(file_obj, max_size_mb=50):
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        raise ValidationError(f'File exceeds {max_size_mb}MB limit')

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    ext = filename.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'File type not allowed')
```

### Secure File Storage

```python
# projects/adapters/views.py
class ProjectFileUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        
        # Validate
        validate_file_size(file, max_size_mb=50)
        validate_file_extension(file.name, ['pdf', 'zip'])
        
        # Generate unique filename
        import uuid
        ext = file.name.split('.')[-1]
        filename = f'{uuid.uuid4()}.{ext}'
        
        # Save to storage
        file.name = filename
        project.file = file
        project.save()
```

---

## Database Security

### Connection Security

```python
# core/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'SSL_REQUIRE': not DEBUG,
    }
}
```

### ORM Security

```python
# ✅ Good - Parameterized queries
User.objects.filter(email=user_email)

# ❌ Bad - String concatenation
User.objects.raw(f"SELECT * FROM users WHERE email = '{user_email}'")
```

---

## Production Deployment

### Environment Configuration

```bash
# .env.production
DEBUG=False
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
ALLOWED_HOSTS=skillsphere.com,www.skillsphere.com
SECURE_SSL_REDIRECT=True
CSRF_TRUSTED_ORIGINS=https://skillsphere.com,https://www.skillsphere.com
```

### Docker Security

```yaml
# docker-compose.yml
services:
  django:
    environment:
      - DEBUG=False
      - SECURE_SSL_REDIRECT=True
    volumes:
      - ./logs:/app/logs
      - ./media:/app/media
    restart: unless-stopped
```

### Security Checklist

- [ ] DEBUG = False in production
- [ ] HTTPS enabled with valid certificate
- [ ] SECRET_KEY is strong and unique
- [ ] All dependencies updated
- [ ] Database encrypted and backed up
- [ ] Logs monitored and archived
- [ ] Rate limiting enabled
- [ ] CORS restricted to allowed origins
- [ ] Security headers configured
- [ ] Regular security audits scheduled
- [ ] Incident response plan in place

---

## Security Testing

### Automated Security Testing

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Django security checks
python manage.py check --deploy
```

### Manual Testing

```bash
# Test CORS
curl -H "Origin: https://malicious.com" https://api.skillsphere.com/api/

# Test rate limiting
for i in {1..150}; do curl https://api.skillsphere.com/api/projects/; done

# Test CSRF protection
curl -X POST https://api.skillsphere.com/api/projects/ \
  -H "Content-Type: application/json"
```

---

## References & Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django REST Framework Security](https://www.django-rest-framework.org/topics/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

## Support & Incident Response

For security issues:
1. Do not disclose publicly
2. Email: security@skillsphere.com
3. Include severity assessment
4. Allow 48 hours for response

Last Updated: July 23, 2026
