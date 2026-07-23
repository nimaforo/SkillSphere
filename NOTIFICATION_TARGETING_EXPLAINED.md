# Notification Targeting - How It Works

## Summary: YES, Notifications Go ONLY to the Specific User! ✅

Each user receives notifications **ONLY** for their own project activities. It's NOT broadcast to everyone.

---

## How It Works

### Architecture

```
User A's Project
     ↓
    ↓ User B likes/comments
    ↓
    └─→ Notification created for User A ONLY
        ├─→ Saved to Database: recipient=User A
        └─→ Sent via WebSocket to User A ONLY (group: notifications_user_1)

User C's Project
     ↓
    ↓ User B likes/comments  
    ↓
    └─→ Notification created for User C ONLY
        ├─→ Saved to Database: recipient=User C
        └─→ Sent via WebSocket to User C ONLY (group: notifications_user_3)
```

### Key Code Points

**1. Backend - Projects Domain Service** (`projects/domain/services.py`)
```python
@staticmethod
def add_comment(project_id, user, text: str):
    project = Project.objects.get(id=project_id)
    comment = ProjectComment.objects.create(...)
    
    if project.user != user:  # ← Only if not self-commenting
        ProjectDomainService._dispatch_notifications(
            recipient_user=project.user,  # ← Send to PROJECT OWNER
            trigger_user=user,
            notif_type="chat",
            ws_message=f"{user.email} روی پروژه شما کامنت گذاشت",
            db_message=f"{user.email} روی پروژه شما کامنت گذاشت",
            project_id=project.id,
            sender_id=user.id
        )
```

**2. Backend - Notification Dispatch** (`projects/domain/services.py`)
```python
@staticmethod
def _dispatch_notifications(...):
    channel_layer = get_channel_layer()
    user_notification_group = f'notifications_user_{recipient_user.id}'  # ← User-specific group!
    
    async_to_sync(channel_layer.group_send)(
        user_notification_group,  # Only this user's WebSocket gets it
        {
            "type": "send_notification",
            "message": ws_message,
            "user_id": recipient_user.id,  # ← Recipient marked
            ...
        }
    )
    
    # Also save to database
    Notification.objects.create(
        recipient=recipient_user,  # ← Only this user in DB
        sender=trigger_user,
        message=db_message,
        notification_type=notif_type
    )
```

**3. Backend - WebSocket Consumer** (`projects/consumers.py`)
```python
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        # Join user-specific group
        self.user_notification_group = f'notifications_user_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.user_notification_group,  # ← Only receive for THIS user
            self.channel_name
        )
    
    async def send_notification(self, event):
        # Double-check this notification is for this user
        if event.get("user_id") == self.user.id:  # ← Security check
            await self.send(text_data=json.dumps({...}))
```

**4. Frontend - Subscribe to Own Notifications** (`App.jsx`)
```javascript
const socketUrl = `ws://127.0.0.1:8000/ws/notifications/?token=${token}`;
let socket = new WebSocket(socketUrl);
// User automatically subscribes to their own group via JWT
```

---

## Test Results - Proof of Targeting

**Scenario 1**: User2 comments on User1's project
```
Result:
  ✅ User1 gets notification
  ❌ User2 gets nothing
  ❌ User3 gets nothing
```

**Scenario 2**: User3 likes User1's project
```
Result:
  ✅ User1 gets notification  
  ❌ User2 gets nothing
  ❌ User3 gets nothing (liker doesn't notify themselves)
```

**Scenario 3**: User1 likes User2's project
```
Result:
  ❌ User1 gets nothing
  ✅ User2 gets notification
  ❌ User3 gets nothing
```

**Final Count**:
- User1: 2 notifications (about their project)
- User2: 1 notification (about their project)
- User3: 0 notifications (nobody acted on their project)

---

## WebSocket Group Structure

Each user has a dedicated WebSocket group:

```
notifications_user_1  ← Only User 1's WebSocket connections join
notifications_user_2  ← Only User 2's WebSocket connections join
notifications_user_3  ← Only User 3's WebSocket connections join
...
```

When a notification is created:
1. System identifies the recipient (e.g., User 1)
2. Sends to group `notifications_user_1` ONLY
3. Only User 1's WebSocket receives it

---

## Database - Also Targeted

```sql
SELECT * FROM users_notification WHERE recipient_id = 1;
-- Returns only notifications FOR User 1

SELECT * FROM users_notification;
-- Shows each notification has a specific recipient_id
```

Example:
```
ID | Recipient | Sender | Message | Type
---|-----------|--------|---------|------
 1 | User1     | User2  | commented | chat
 2 | User1     | User3  | liked | like
 3 | User2     | User1  | liked | like
```

User1's notifications (IDs 1,2) are ONLY in their list, not broadcast.

---

## Flow Diagram: How a Notification Gets to Right User

```
User2 likes User1's project
        ↓
ProjectCommentView.post()
        ↓
ProjectDomainService.toggle_like(project_id, user2)
        ↓
Notification created with:
  recipient = User1  ← KEY: Specific recipient!
  sender = User2
        ↓
_dispatch_notifications() called
        ↓
┌─────────────────────────────────────────┐
│ Split into two paths:                   │
├─────────────────────────────────────────┤
│ Path 1: WebSocket (Real-time)           │
│  group = "notifications_user_1"         │
│  Sent to User1's WebSocket ONLY         │
│                                         │
│ Path 2: Database (Persistent)           │
│  Notification.objects.create(           │
│    recipient_id = 1                     │
│  )                                      │
└─────────────────────────────────────────┘
        ↓
User1 sees notification in:
  1) Real-time dropdown (via WebSocket)
  2) API endpoint /api/projects/notifications/
```

---

## Security Verification

Two layers ensure targeting:

**Layer 1: Channel Group Targeting**
- WebSocket message sent to `notifications_user_1` group
- Only User1's connections in that group

**Layer 2: Event Validation**
```python
if event.get("user_id") == self.user.id:
    # Only send if notification is for THIS user
    await self.send(...)
```

---

## To Verify in Real Usage

**Setup:**
1. Create User A and User B
2. Both login (separate browsers/incognito)
3. User A creates project
4. User B likes/comments on User A's project

**Expected:**
- ✅ User A sees notification
- ✅ User B sees nothing
- ✅ Check database: only User A in recipient_id

**Network Check:**
- User A WebSocket: Gets group `notifications_user_{A.id}`
- User B WebSocket: Gets group `notifications_user_{B.id}`
- Message only sent to User A's group

---

## Conclusion

**YES - Notifications are 100% targeted to specific users!**

- ✅ Not broadcast to all users
- ✅ Each user gets only notifications about their projects
- ✅ Verified by database test
- ✅ Secured by JWT authentication
- ✅ WebSocket groups ensure isolation

**You can trust that when User B likes User A's project, ONLY User A receives the notification, not everyone!** 🎯
