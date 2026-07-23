#!/usr/bin/env python
"""Quick WebSocket connection test to check authentication"""
import sys
import time

# Tokens from earlier
TOKEN_USER1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg0OTEwMjUyLCJpYXQiOjE3ODQ4MjM4NTIsImp0aSI6ImNmZjE1ZTM3YWU1ZjQyYmFhZGFiNGVmZGQxOThiZGQ3IiwidXNlcl9pZCI6IjEifQ.AbGQm58dk97rg7Hle5NhJxcoKkJCO-Ts1DUOYtTXMlQ"

print("Notifications WebSocket URL (copy to browser console):")
print(f"ws://localhost:8000/ws/notifications/?token={TOKEN_USER1}")
print("\nChat WebSocket URL (copy to browser console, project_id=1):")
print(f"ws://localhost:8000/ws/chat/1/?token={TOKEN_USER1}")
print("\nCheck Django logs for authentication debug messages...")
print("\nRun this in browser console to test:")
print("""
const ws = new WebSocket('ws://localhost:8000/ws/notifications/?token=""" + TOKEN_USER1 + """');
ws.onopen = () => console.log('✅ Connected');
ws.onerror = (e) => console.error('❌ Error', e);
ws.onmessage = (e) => console.log('📨 Message:', e.data);
ws.onclose = () => console.log('🔌 Closed');
""")
