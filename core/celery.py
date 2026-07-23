# core/celery.py
import os
from celery import Celery

# تنظیم ماژول پیش‌فرض تنظیمات جنگو برای Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# استفاده از تنظیمات جنگو با پیشوند CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# لود کردن خودکار تسک‌ها از تمام اپلیکیشن‌های نصب شده
app.autodiscover_tasks()