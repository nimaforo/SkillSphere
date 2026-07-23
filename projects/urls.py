# projects/urls.py
from django.urls import path
from .adapters.views import (
    ProjectFileUploadView,
    ProjectFeedView,
    LikeProjectView,
    ProjectCommentView,
    SecureProjectDownloadView,
    NotificationListView,
    ClearNotificationView,
    MarkNotificationAsReadView,
    SystemAnalyticsView,
    UserAnalyticsView
)

urlpatterns = [
    # 📤 Project Upload
    path('upload/', ProjectFileUploadView.as_view(), name='project-upload'),
    
    # 📋 Project Feed
    path('feed/', ProjectFeedView.as_view(), name='project-feed'),
    
    # ❤️ Like/Unlike
    path('feed/<int:project_id>/like/', LikeProjectView.as_view(), name='like-project'),
    
    # 💬 Comments
    path('feed/<int:project_id>/comment/', ProjectCommentView.as_view(), name='project-comment'),
    
    # 📥 Download
    path('feed/<int:project_id>/download/', SecureProjectDownloadView.as_view(), name='secure-download-project'),
    
    # 🔔 Notifications
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('notifications/<int:notification_id>/delete/', ClearNotificationView.as_view(), name='delete-notification'),
    path('notifications/clear-all/', ClearNotificationView.as_view(), name='clear-all-notifications'),
    
    # 📊 Analytics
    path('analytics/', SystemAnalyticsView.as_view(), name='system-analytics'),
    path('user-analytics/', UserAnalyticsView.as_view(), name='user-analytics'),
]

