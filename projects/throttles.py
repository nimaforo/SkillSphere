# projects/throttles.py
from rest_framework.throttling import UserRateThrottle

class UploadBurstThrottle(UserRateThrottle):
    """جلوگیری از هجوم آپلودهای فیک و پر شدن هارد کانتینر داکر"""
    scope = 'uploads'

class ActionBurstThrottle(UserRateThrottle):
    """جلوگیری از اسپم لایک، کامنت و شلیک بی‌رویه نوتیفیکیشن وب‌سوکت"""
    scope = 'actions'