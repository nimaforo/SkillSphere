#!/usr/bin/env python
"""Create test notifications to verify the system works"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Notification
from projects.models import Project

User = get_user_model()

print('\n=== CREATING TEST NOTIFICATIONS ===\n')

users = User.objects.all()
if len(users) < 2:
    print('⚠️ Need at least 2 users to create notifications')
    print('Creating second test user...')
    user2, _ = User.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'testuser2@example.com'}
    )
    user2.set_password('password123')
    user2.save()
    print(f'✅ Created: {user2.email}')
else:
    user2 = users[1]

user1 = users[0]

print(f'User 1: {user1.email}')
print(f'User 2: {user2.email}')

# Create test notifications
notif1 = Notification.objects.create(
    recipient=user1,
    sender=user2,
    notification_type='like',
    message=f'{user2.email} پروژه شما را لایک کرد ❤️'
)

notif2 = Notification.objects.create(
    recipient=user1,
    sender=user2,
    notification_type='chat',
    message=f'{user2.email} روی پروژه شما کامنت گذاشت 💬'
)

print(f'\n✅ Created 2 test notifications')
print(f'\nNotifications in database:')
for n in Notification.objects.all():
    sender_email = n.sender.email if n.sender else 'System'
    print(f'  - To: {n.recipient.email}, From: {sender_email}, Type: {n.notification_type}')
    print(f'    Message: {n.message}')

print('\n=== TESTING NOTIFICATIONS ENDPOINT ===\n')

from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from projects.adapters.views import NotificationListView

factory = APIRequestFactory()
refresh = RefreshToken.for_user(user1)
access_token = str(refresh.access_token)

# Create authenticated request
request = factory.get('/api/projects/notifications/')
request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
request.user = user1

# Call the view
view = NotificationListView.as_view()
response = view(request)

print(f'Endpoint Status: {response.status_code}')
print(f'Response: {response.data}')

print('\n✅ Test complete! Notifications should now appear in the app.')
