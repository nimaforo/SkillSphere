import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', "django-insecure-rjc9t4@+n*630u1s)5d60$kkv&rm*!nqlbo8#l5_6io0p#4cla")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition
INSTALLED_APPS = [
    'daphne',  # باید اولین آیتم باشد برای Django Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # پکیج‌های ثالث
    'rest_framework',
    'django_celery_results',
    'drf_spectacular',
    'corsheaders',
    
    # اپلیکیشن‌های پروژه
    'users',
    'projects',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.activity_middleware.ActivityTrackingMiddleware',
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = 'core.asgi.application'


# Database - PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        "NAME": os.getenv('DB_NAME', BASE_DIR / "db.sqlite3"),
        "USER": os.getenv('DB_USER', ''),
        "PASSWORD": os.getenv('DB_PASSWORD', ''),
        "HOST": os.getenv('DB_HOST', 'localhost'),
        "PORT": os.getenv('DB_PORT', '5432'),
        
        # Connection pooling (optional)
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static and Media Files
STATIC_URL = "static/"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = 'users.UserModel'


# 🌟 تنظیمات یکپارچه CORS (حل تداخل پورت ۵۱۷۳ و داکر)
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
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

# Security Settings - Development
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    # Production Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security Headers (All Environments)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'", "https:"),
    'script-src': ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"),
    'style-src': ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"),
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'", "https:"),
    'connect-src': ("'self'", "https:", "wss:"),
}

# HSTS (HTTP Strict Transport Security)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# X-Frame-Options
X_FRAME_OPTIONS = 'DENY'

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')

# Security Middleware
MIDDLEWARE.insert(0, 'django.middleware.security.SecurityMiddleware')
CACHES = {
    "default": {
        "BACKEND": os.getenv('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache'),
        "LOCATION": os.getenv('CACHE_LOCATION', 'skill-sphere-local-cache'),
        "TIMEOUT": 300,  # 5 minutes
    }
}

# 🌟 تنظیمات Django Rest Framework (تجمیع شده و بدون تداخل)
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    
    # Rate Limiting & Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',           # Anonymous: 100 requests/hour
        'user': '1000/hour',          # Authenticated: 1000 requests/hour
        'uploads': '5/hour',          # File uploads: 5/hour
        'notifications': '50/hour',   # Notifications: 50/hour
    },
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Filtering & Search
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Exception Handling
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    
    # JSON Formatting
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    
    # Versioning (disabled for now - use query params if needed)
    'DEFAULT_VERSIONING_CLASS': None,
    # 'ALLOWED_VERSIONS': ['1.0', '1.1'],
    # 'VERSION_PARAM': 'version',
    
    # API Settings
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
}


# 🌟 تنظیمات SimpleJWT (یکپارچه و طولانی‌مدت برای محیط توسعه)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# 🌟 Celery Settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule (Periodic Tasks)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # روزانہ کی سرگرمیاں - رات 2 بجے
    'daily-tasks': {
        'task': 'projects.tasks.daily_tasks',
        'schedule': crontab(hour=2, minute=0),
    },
    # ہفتہ وار سرگرمیاں - ہفتہ کو صبح 9 بجے
    'weekly-tasks': {
        'task': 'projects.tasks.weekly_tasks',
        'schedule': crontab(day_of_week=6, hour=9, minute=0),  # Saturday at 9 AM
    },
    # پرانے اعلان صاف کریں - ہر ہفتہ
    'cleanup-notifications': {
        'task': 'projects.tasks.cleanup_old_notifications',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sunday at 3 AM
    },
    # غیر فعال فائلیں حذف کریں - ہر ہفتہ
    'cleanup-files': {
        'task': 'projects.tasks.cleanup_orphaned_files',
        'schedule': crontab(day_of_week=1, hour=4, minute=0),  # Monday at 4 AM
    },
    # غیر فعال اکاؤنٹ - ہر ماہ
    'deactivate-inactive': {
        'task': 'users.tasks.deactivate_inactive_accounts',
        'schedule': crontab(day_of_month=1, hour=5, minute=0),  # First day of month at 5 AM
    },
}

# Celery Task Routes (مختلف queues میں tasks بھیجیں)
CELERY_TASK_ROUTES = {
    'projects.tasks.send_notification_email': {'queue': 'emails'},
    'projects.tasks.send_bulk_notification_emails': {'queue': 'emails'},
    'users.tasks.send_welcome_email': {'queue': 'emails'},
    'users.tasks.send_password_reset_email': {'queue': 'emails'},
    'projects.tasks.generate_project_thumbnail': {'queue': 'processing'},
    'projects.tasks.compress_project_file': {'queue': 'processing'},
}

# Celery Task Configuration
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_TASK_ALWAYS_EAGER = False  # Set True for testing
CELERY_TASK_EAGER_PROPAGATES = True

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@skillsphere.com')

# Frontend URL for reset links etc
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')


# Documentation Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'SkillSphere API Project',
    'DESCRIPTION': 'مستندات کامل ابزارها و وب‌سرویس‌های پروژه پلتفرم مهارتی SkillSphere',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# Channels / Chat Layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


# ========================
# 📝 LOGGING CONFIGURATION
# ========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Create logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)


# ========================
# 🔐 Google OAuth2 Configuration
# ========================
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', '')

# ========================
# 🔍 Elasticsearch Configuration
# ========================
ELASTICSEARCH_HOSTS = os.getenv('ELASTICSEARCH_HOSTS', 'localhost:9200').split(',')
ELASTICSEARCH_INDEX_PREFIX = 'skillsphere'
