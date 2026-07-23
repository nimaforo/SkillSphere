#!/usr/bin/env python
"""
Celery Tasks کو test کریں
django shell میں چلائیں: python manage.py shell < test_celery_tasks.py
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project
from users.models import Notification
from projects.tasks import (
    send_notification_email,
    generate_user_analytics_report,
    generate_system_analytics_report,
    cleanup_old_notifications
)
from users.tasks import (
    send_welcome_email,
    calculate_user_statistics
)
import logging

User = get_user_model()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("🧪 Celery Tasks ٹیسٹ")
print("=" * 80)

# صارفین بنائیں
user1, _ = User.objects.get_or_create(
    email='celerytest1@example.com',
    defaults={'username': 'celerytest1', 'first_name': 'Celery ٹیسٹ 1'}
)

user2, _ = User.objects.get_or_create(
    email='celerytest2@example.com',
    defaults={'username': 'celerytest2', 'first_name': 'Celery ٹیسٹ 2'}
)

print(f"\n✅ صارفین بنائے گئے:")
print(f"   - {user1.email}")
print(f"   - {user2.email}")

# پروژہ بنائیں
project, created = Project.objects.get_or_create(
    user=user1,
    title='Celery ٹیسٹ پروژہ',
    defaults={'description': 'ٹیسٹنگ کے لیے'}
)

print(f"\n✅ پروژہ: {project.title} (ID: {project.id})")

# اعلان بنائیں
notification, created = Notification.objects.get_or_create(
    recipient=user1,
    message='Celery ٹیسٹ اعلان',
    defaults={'notification_type': 'like', 'sender': user2}
)

print(f"✅ اعلان: {notification.message}")

print("\n" + "=" * 80)
print("📧 Email Tasks ٹیسٹ")
print("=" * 80)

# Welcome email
print("\n1️⃣ خوش آمدید ای‌میل:")
result = send_welcome_email.apply_async(args=[user1.id])
print(f"   Task ID: {result.id}")
print(f"   Status: {result.status}")

# Notification email
print("\n2️⃣ اعلان ای‌میل:")
result = send_notification_email.apply_async(args=[notification.id])
print(f"   Task ID: {result.id}")
print(f"   Status: {result.status}")

print("\n" + "=" * 80)
print("📊 Analytics Tasks ٹیسٹ")
print("=" * 80)

# User analytics
print("\n1️⃣ صارف تحلیلات:")
try:
    stats = generate_user_analytics_report(user1.id)
    print(f"   نتیجہ: {stats}")
except Exception as e:
    print(f"   ❌ خرابی: {str(e)}")

# System analytics
print("\n2️⃣ سسٹم تحلیلات:")
try:
    stats = generate_system_analytics_report()
    print(f"   نتیجہ: {stats}")
except Exception as e:
    print(f"   ❌ خرابی: {str(e)}")

# User statistics
print("\n3️⃣ صارف کے اعدادوشمار:")
try:
    stats = calculate_user_statistics(user1.id)
    print(f"   پروژے: {stats.get('projects_count', 0)}")
    print(f"   لائکس: {stats.get('total_likes', 0)}")
    print(f"   اعلانات: {stats.get('notifications', 0)}")
except Exception as e:
    print(f"   ❌ خرابی: {str(e)}")

print("\n" + "=" * 80)
print("🧹 Cleanup Tasks ٹیسٹ")
print("=" * 80)

# Cleanup
print("\n1️⃣ پرانے اعلانات صاف کریں:")
try:
    result = cleanup_old_notifications(days=0)  # صرف ٹیسٹ کے لیے
    print(f"   نتیجہ: {result}")
except Exception as e:
    print(f"   ❌ خرابی: {str(e)}")

print("\n" + "=" * 80)
print("✅ تمام ٹیسٹ مکمل!")
print("=" * 80)

print("\n💡 اگلے اقدام:")
print("   1. Celery worker شروع کریں:")
print("      celery -A core worker -l info")
print("\n   2. Celery Beat شروع کریں (scheduled tasks کے لیے):")
print("      celery -A core beat -l info")
print("\n   3. Redis شروع کریں:")
print("      redis-cli")
