# core/asgi.py
import os
import django
from django.core.asgi import get_asgi_application

# ۱. ابتدا متغیر محیطی تنظیمات جنگو را ست می‌کنیم
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# ۲. پروکسی اصلی HTTP را لود و جنگو را آماده‌سازی می‌کنیم
django_asgi_app = get_asgi_application()

# ۳. حالا که اپلیکیشن‌ها کاملاً لود شده‌اند، پکیج‌های Channels و میدل‌ورها را ایمپورت می‌کنیم 🚀
from channels.routing import ProtocolTypeRouter, URLRouter
import projects.routing 
from projects.middleware import JwtAuthMiddleware  

# ۴. ساختار روتر پروتکل‌ها را مقداردهی می‌کنیم
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddleware(  
        URLRouter(
            projects.routing.websocket_urlpatterns
        )
    ),
})