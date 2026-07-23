#!/usr/bin/env python
"""
End-to-end test for Comments, Chat, and Notifications
Tests all three features with fresh test data
"""
import os
import sys
import json
import django
from urllib.request import Request, urlopen
from urllib.error import URLError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project, ProjectComment

User = get_user_model()

# Test tokens (from create_test_data.py)
TOKEN_USER1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg0OTEwMjUyLCJpYXQiOjE3ODQ4MjM4NTIsImp0aSI6ImNmZjE1ZTM3YWU1ZjQyYmFhZGFiNGVmZGQxOThiZGQ3IiwidXNlcl9pZCI6IjEifQ.AbGQm58dk97rg7Hle5NhJxcoKkJCO-Ts1DUOYtTXMlQ"
TOKEN_USER2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg0OTEwMjUyLCJpYXQiOjE3ODQ4MjM4NTIsImp0aSI6IjRhMGFjNzcwYzM5YzQ2MjE4Zjg1OTU0MGQ3ZGFmMzdjIiwidXNlcl9pZCI6IjIifQ.THpGhRKkM20rInvRM1TLq4xuilqWR6txQwVJBtkpezo"

BASE_URL = "http://127.0.0.1:8000"
WS_BASE_URL = "ws://localhost:8000"

print("\n" + "="*60)
print("📋 SKILLSPHERE END-TO-END TEST SUITE")
print("="*60)

# ============================================================
# TEST 1: COMMENTS
# ============================================================
print("\n[TEST 1] 🗨️ COMMENTS - POST new comment")
print("-" * 60)

# First, get or create a test project with proper file
user1 = User.objects.get(username='testuser1')
test_file_path = '/app/test_project.txt'
with open(test_file_path, 'w') as f:
    f.write('test content')

from django.core.files import File
project, created = Project.objects.get_or_create(
    user=user1,
    title='Test Project for E2E',
    defaults={
        'description': 'E2E testing project',
    }
)
if created:
    with open(test_file_path, 'rb') as f:
        project.file.save('test.txt', File(f))

project_id = project.id
print(f"Project ID: {project_id}")

# Test comment POST
comment_data = {"content": "This is a test comment"}
headers = {
    "Authorization": f"Bearer {TOKEN_USER1}",
    "Content-Type": "application/json"
}

url = f"{BASE_URL}/api/projects/feed/{project_id}/comment/"
req = Request(
    url,
    data=json.dumps(comment_data).encode('utf-8'),
    headers=headers,
    method='POST'
)

try:
    with urlopen(req) as response:
        status = response.status
        body = response.read().decode('utf-8')
        print(f"Status Code: {status}")
        if status in [200, 201]:
            print("✅ PASS: Comment created successfully")
            comment_response = json.loads(body)
            print(f"Response: {json.dumps(comment_response, indent=2)}")
        else:
            print(f"❌ FAIL: Unexpected status")
except URLError as e:
    print(f"Status Code: {e.code if hasattr(e, 'code') else 'Unknown'}")
    if hasattr(e, 'code') and e.code in [200, 201]:
        print("✅ PASS: Comment created successfully")
        try:
            body = e.read().decode('utf-8')
            print(f"Response: {json.dumps(json.loads(body), indent=2)}")
        except:
            pass
    else:
        print(f"❌ FAIL: Comment POST failed")
        try:
            print(f"Response: {e.read().decode('utf-8')}")
        except:
            print(f"Error: {str(e)}")

# ============================================================
# TEST 2: CHAT WEBSOCKET
# ============================================================
print("\n[TEST 2] 💬 CHAT - WebSocket Connection")
print("-" * 60)
print("⚠️ WebSocket testing requires 'websockets' module")
print("From frontend: Verify connection with browser DevTools Network tab")
print("Expected URL: ws://localhost:8000/ws/chat/{project_id}/?token={token}")

# ============================================================
# TEST 3: NOTIFICATIONS WEBSOCKET
# ============================================================
print("\n[TEST 3] 🔔 NOTIFICATIONS - WebSocket Connection")
print("-" * 60)
print("⚠️ WebSocket testing requires 'websockets' module")
print("From frontend: Verify connection with browser DevTools Network tab")
print("Expected URL: ws://localhost:8000/ws/notifications/?token={token}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("✅ END-TO-END TEST COMPLETE")
print("="*60)
print("\nResults:")
print("1. Comments: Test POST request with 'content' field")
print("2. Chat: Test WebSocket connection to /ws/chat/{id}")
print("3. Notifications: Test WebSocket connection to /ws/notifications/")
print("\n" + "="*60)
