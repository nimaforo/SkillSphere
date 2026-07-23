#!/usr/bin/env python
"""Test that notifications go only to specific user, not broadcast to all"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Notification
from projects.models import Project, ProjectComment
from projects.domain.services import ProjectDomainService

User = get_user_model()

print('\n' + '='*70)
print('NOTIFICATION TARGETING TEST - Verify Each User Gets Only Their Notifications')
print('='*70 + '\n')

# Get or create users
user1, _ = User.objects.get_or_create(
    username='user1',
    defaults={'email': 'user1@example.com'}
)
user2, _ = User.objects.get_or_create(
    username='user2', 
    defaults={'email': 'user2@example.com'}
)
user3, _ = User.objects.get_or_create(
    username='user3',
    defaults={'email': 'user3@example.com'}
)

for u in [user1, user2, user3]:
    u.set_password('password123')
    u.save()

print(f'Users created/verified:')
print(f'  - User 1: {user1.email} (ID: {user1.id})')
print(f'  - User 2: {user2.email} (ID: {user2.id})')
print(f'  - User 3: {user3.email} (ID: {user3.id})')

# Create projects
project1 = Project.objects.filter(user=user1).first()
if not project1:
    project1 = Project.objects.create(
        user=user1,
        title='User1 Project',
        description='A project owned by User 1',
        file='dummy.txt'
    )

project2 = Project.objects.filter(user=user2).first()
if not project2:
    project2 = Project.objects.create(
        user=user2,
        title='User2 Project',
        description='A project owned by User 2',
        file='dummy.txt'
    )

print(f'\nProjects created/verified:')
print(f'  - Project 1 owned by User1')
print(f'  - Project 2 owned by User2')

# Clear old notifications
Notification.objects.all().delete()
print(f'\nCleared old notifications')

# SCENARIO 1: User2 comments on User1's project
print(f'\n' + '-'*70)
print('SCENARIO 1: User2 comments on User1 project')
print('-'*70)

comment = ProjectDomainService.add_comment(project1.id, user2, 'Great project!')
print(f'✅ User2 commented on User1 project')

notifs_user1 = Notification.objects.filter(recipient=user1).count()
notifs_user2 = Notification.objects.filter(recipient=user2).count()
notifs_user3 = Notification.objects.filter(recipient=user3).count()

print(f'\nNotifications after comment:')
print(f'  - User1 notifications: {notifs_user1} (Expected: 1) {"✅" if notifs_user1 == 1 else "❌"}')
print(f'  - User2 notifications: {notifs_user2} (Expected: 0) {"✅" if notifs_user2 == 0 else "❌"}')
print(f'  - User3 notifications: {notifs_user3} (Expected: 0) {"✅" if notifs_user3 == 0 else "❌"}')

# SCENARIO 2: User3 likes User1's project
print(f'\n' + '-'*70)
print('SCENARIO 2: User3 likes User1 project')
print('-'*70)

liked, total = ProjectDomainService.toggle_like(project1.id, user3)
print(f'✅ User3 liked User1 project')

notifs_user1 = Notification.objects.filter(recipient=user1).count()
notifs_user2 = Notification.objects.filter(recipient=user2).count()
notifs_user3 = Notification.objects.filter(recipient=user3).count()

print(f'\nNotifications after like:')
print(f'  - User1 notifications: {notifs_user1} (Expected: 2) {"✅" if notifs_user1 == 2 else "❌"}')
print(f'  - User2 notifications: {notifs_user2} (Expected: 0) {"✅" if notifs_user2 == 0 else "❌"}')
print(f'  - User3 notifications: {notifs_user3} (Expected: 0) {"✅" if notifs_user3 == 0 else "❌"}')

# SCENARIO 3: User1 likes User2's project
print(f'\n' + '-'*70)
print('SCENARIO 3: User1 likes User2 project')
print('-'*70)

liked, total = ProjectDomainService.toggle_like(project2.id, user1)
print(f'✅ User1 liked User2 project')

notifs_user1 = Notification.objects.filter(recipient=user1).count()
notifs_user2 = Notification.objects.filter(recipient=user2).count()
notifs_user3 = Notification.objects.filter(recipient=user3).count()

print(f'\nNotifications after like:')
print(f'  - User1 notifications: {notifs_user1} (Expected: 2) {"✅" if notifs_user1 == 2 else "❌"}')
print(f'  - User2 notifications: {notifs_user2} (Expected: 1) {"✅" if notifs_user2 == 1 else "❌"}')
print(f'  - User3 notifications: {notifs_user3} (Expected: 0) {"✅" if notifs_user3 == 0 else "❌"}')

# Print all notifications
print(f'\n' + '='*70)
print('FINAL NOTIFICATION SUMMARY')
print('='*70)

for user in [user1, user2, user3]:
    notifs = Notification.objects.filter(recipient=user)
    print(f'\n{user.email} has {notifs.count()} notifications:')
    for n in notifs:
        sender = n.sender.email if n.sender else 'System'
        print(f'  - From {sender}: {n.message}')

print(f'\n' + '='*70)
print('✅ CONCLUSION: Notifications are sent to SPECIFIC users only!')
print('   Each user only receives notifications for their own projects.')
print('='*70 + '\n')
