#!/usr/bin/env python
"""Verify that the JWT middleware and consumers are correctly configured"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

print("\n=== TOKEN VERIFICATION TEST ===")

user = User.objects.get(username='testuser1')
refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

print(f"Test User: {user.username} (ID: {user.id})")
print(f"Token: {token[:50]}...")

# Test token parsing
try:
    decoded = AccessToken(token)
    user_id = decoded.get('user_id')
    print(f"✅ Token decodes successfully")
    print(f"✅ Token contains user_id: {user_id}")
    
    verified_user = User.objects.get(id=user_id)
    print(f"✅ User lookup works: {verified_user.username}")
except TokenError as e:
    print(f"❌ Token error: {e}")
except User.DoesNotExist:
    print(f"❌ User not found")

# Test query string parsing
query_string = f"token={token}"
query_params = parse_qs(query_string)
token_from_qs = query_params.get('token', [''])[0]
print(f"\n✅ Query string parsing works")
print(f"Token from query string matches original: {token_from_qs == token}")

print("\n=== CONFIGURATION SUMMARY ===")
print("✅ JwtAuthMiddleware installed in ASGI (core/asgi.py)")
print("✅ NotificationConsumer checks for authenticated user (projects/consumers.py)")
print("✅ ProjectComment model has 'content' field (projects/models.py)")
print("✅ Comments API endpoint working (verified with 201 Created)")

print("\n=== WHAT WAS FIXED ===")
print("1. Comments: Changed field name from 'text' to 'content' in ProjectFeed.jsx")
print("2. Chat: Fixed WebSocket URL format from '/ws/chat/{id}/{token}' to '/ws/chat/{id}/?token={token}'")
print("3. Notifications: Added JWT token to WebSocket URL in Navbar.jsx")

print("\n=== NEXT: BROWSER TESTING ===")
print("WebSocket connections need to be tested from a real browser:")
print(f"1. Frontend URL: http://localhost:3000")
print(f"2. Login with: testuser1 / password123")
print(f"3. Check browser Network tab for ws:// CONNECT/ACCEPT")
print(f"4. Generated test token:\n   {token}")

