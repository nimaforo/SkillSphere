#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project, ProjectComment

User = get_user_model()

# Create test user
user = User.objects.create_user(
    email='test@example.com',
    username='testuser',
    password='testpass123',
    first_name='Test'
)
print(f'✅ Created user: {user.email} (name: {user.first_name})')

# Create test project
project = Project.objects.create(
    title='My First Project',
    description='Test project for the dashboard',
    user=user,
    file='project_files/sample.pdf'
)
print(f'✅ Created project: {project.title}')

# Add some likes
project.likes.add(user)
print(f'✅ Added like to project')

# Create test comment
comment = ProjectComment.objects.create(
    project=project,
    user=user,
    content='This is a test comment on my project'
)
print(f'✅ Created comment: {comment.content[:30]}...')

print(f'\n📊 Database Summary:')
print(f'Total Users: {User.objects.count()}')
print(f'Total Projects: {Project.objects.count()}')
print(f'Total Comments: {ProjectComment.objects.count()}')
