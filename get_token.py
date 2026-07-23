#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
users = User.objects.all()
if users.exists():
    user = users.first()
    refresh = RefreshToken.for_user(user)
    print(f"User: {user.username}")
    print(f"AccessToken: {str(refresh.access_token)}")
else:
    print("No users found")
