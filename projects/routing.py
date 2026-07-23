# projects/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # 🌟 اصلاح شد: تبدیل as_view به as_asgi
    path('ws/chat/<int:project_id>/', consumers.ChatConsumer.as_asgi()), 
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]