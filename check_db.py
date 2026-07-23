#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Notification
from projects.models import Project, ProjectComment

User = get_user_model()

print('\n=== DATABASE STATUS ===\n')

# Check users
users = User.objects.all()
print(f'Users: {users.count()}')
for u in users:
    print(f'  - {u.email} (id={u.id})')

# Check projects
projects = Project.objects.all()
print(f'\nProjects: {projects.count()}')
for p in projects:
    print(f'  - {p.title} by {p.user.email} (id={p.id})')

# Check comments
comments = ProjectComment.objects.all()
print(f'\nComments: {comments.count()}')
for c in comments:
    print(f'  - {c.user.email}: {c.content[:40]}...')

# Check notifications
notifs = Notification.objects.all()
print(f'\nNotifications in DB: {notifs.count()}')
for n in notifs:
    sender_email = n.sender.email if n.sender else 'System'
    print(f'  - To: {n.recipient.email}, From: {sender_email}, Type: {n.notification_type}')
    print(f'    Message: {n.message[:50]}...')

print('\n=== API ENDPOINTS CHECK ===\n')

# Test the notification endpoint
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

client = APIClient()
user = User.objects.first()

if user:
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test notifications endpoint
    print('Testing: GET /api/projects/notifications/')
    response = client.get('/api/projects/notifications/')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Response: {data}')
    else:
        print(f'Error: {response.data}')
else:
    print('No users found in database')
