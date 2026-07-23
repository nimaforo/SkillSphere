# 🎯 Activity Tracking - Updated

## Changes Made

### Activity Log Model Redesigned
**File:** `users/models.py`

**Old Model:** Tracked HTTP requests (path, method, status_code, duration, IP)
**New Model:** Tracks meaningful user actions on projects

#### New UserActivityLog Fields:
```python
- user: ForeignKey to User (nullable)
- activity_type: Choice field
    * 'project_upload' - When user uploads a project
    * 'project_like' - When user likes a project
    * 'project_comment' - When user comments on a project
- project: ForeignKey to Project (nullable)
- description: CharField (for details)
- created_at: DateTimeField (auto timestamp)
```

---

## Activity Types

### 1. Project Upload 📤
**When:** User successfully uploads a new project
**Logged in:** `ProjectFileUploadView.post()`
```python
UserActivityLog.objects.create(
    user=request.user,
    activity_type='project_upload',
    project=project,
    description=f'Uploaded project: {project.title}'
)
```

### 2. Project Like ❤️
**When:** User likes a project (but NOT when they unlike)
**Logged in:** `LikeProjectView.post()`
```python
if liked:  # Only log on like, not unlike
    UserActivityLog.objects.create(
        user=request.user,
        activity_type='project_like',
        project=project,
        description=f'Liked project: {project.title}'
    )
```

### 3. Project Comment 💬
**When:** User adds a comment to a project
**Logged in:** `ProjectCommentView.post()`
```python
UserActivityLog.objects.create(
    user=request.user,
    activity_type='project_comment',
    project=project,
    description=f'Commented on project: {project.title}'
)
```

---

## Analytics Updates

### Profile Analytics
**Endpoint:** `GET /api/users/profile/`

**recent_activity_7days:** Now counts only:
- Project uploads by user
- Project likes by user
- Comments by user
(Within last 7 days)

### System Analytics
**Endpoint:** `GET /api/projects/analytics/`

**active_users:** Now based on actual activity (project uploads, likes, comments)

### User Analytics
**Endpoint:** `GET /api/projects/user-analytics/`

**New fields in response:**
```json
{
  "activities": {
    "project_uploads": 3,
    "project_likes_given": 5,
    "project_comments_given": 2
  },
  "activity_breakdown": {
    "project_upload": 3,
    "project_like": 5,
    "project_comment": 2
  }
}
```

---

## Database Migration

**Migration File:** `users/migrations/0006_alter_useractivitylog_options_and_more.py`

**Changes:**
- Removed: path, method, status_code, duration, ip_address
- Added: activity_type (CharField with choices)
- Added: project (ForeignKey)
- Added: description (CharField)
- Modified: user (now nullable)
- Added Meta ordering by -created_at

**Status:** ✅ Applied successfully

---

## Benefits

✅ More meaningful activity tracking
✅ No tracking of every HTTP request (cleaner data)
✅ Only tracks actual user actions on projects
✅ Easy to query activities by type
✅ Better performance (fewer log entries)
✅ Provides detailed analytics

---

## Example Usage

### Get user's 7-day activity
```python
from users.models import UserActivityLog
from django.utils import timezone
from datetime import timedelta

last_7_days = timezone.now() - timedelta(days=7)
activities = UserActivityLog.objects.filter(
    user=user,
    created_at__gte=last_7_days
)

# Count by type
uploads = activities.filter(activity_type='project_upload').count()
likes = activities.filter(activity_type='project_like').count()
comments = activities.filter(activity_type='project_comment').count()
```

### Get all projects a user has interacted with
```python
activities = UserActivityLog.objects.filter(user=user)
projects = activities.values_list('project_id', flat=True).distinct()
```

---

## Frontend Display

Profile page now shows:
- **Recent Activity (7 days):** Count of uploads + likes + comments
- **Engagement Score:** Based on actual interactions
- **Activity Breakdown:** Visible through API

---

**Status:** ✅ COMPLETE
**Database:** ✅ MIGRATED
**API:** ✅ UPDATED
**Frontend:** ✅ READY
