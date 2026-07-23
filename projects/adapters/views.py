# projects/adapters/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from django.http import FileResponse, JsonResponse
from django.core.files.storage import default_storage
from django.db.models import Q, Count
from datetime import timedelta
from django.utils import timezone

from projects.models import Project, ProjectComment
from users.models import Notification, UserActivityLog
from projects.domain.services import ProjectDomainService
from .serializers import ProjectCreateSerializer


# ========================
# 📤 Project Upload
# ========================
class ProjectFileUploadView(APIView):
    """پروژه جدید آپلود کن"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                project = serializer.save()
                
                # Log activity
                from users.models import UserActivityLog
                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type='project_upload',
                    project=project,
                    description=f'Uploaded project: {project.title}'
                )
                
                return Response({
                    'message': 'پروژه با موفقیت آپلود شد',
                    'project_id': project.id,
                    'title': project.title,
                    'file_url': project.file.url
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'message': f'خطا در آپلود: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========================
# 📋 Project Feed
# ========================
class ProjectFeedView(APIView):
    """تمام پروژه‌ها را نمایش بده - Public access"""
    permission_classes = []  # Allow unauthenticated access

    def get(self, request):
        # پیجینگ
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        offset = (page - 1) * limit

        projects = Project.objects.select_related('user').annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        ).order_by('-created_at')[offset:offset + limit]

        data = []
        for project in projects:
            # Get comments for this project
            comments = project.comments.select_related('user').order_by('-created_at')
            comments_data = []
            for comment in comments:
                comments_data.append({
                    'id': comment.id,
                    'content': comment.content,
                    'user': {
                        'id': comment.user.id,
                        'email': comment.user.email,
                        'name': comment.user.first_name or comment.user.username
                    },
                    'created_at': comment.created_at.isoformat()
                })
            
            data.append({
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'user': {
                    'id': project.user.id,
                    'email': project.user.email,
                    'name': project.user.first_name or project.user.username
                },
                'file_url': project.file.url if project.file else None,
                'likes_count': project.like_count,
                'comments_count': project.comment_count,
                'comments': comments_data,
                'is_liked_by_user': request.user in project.likes.all() if request.user.is_authenticated else False,
                'created_at': project.created_at.isoformat(),
                'download_url': f'/api/projects/feed/{project.id}/download/'
            })

        return Response({
            'count': Project.objects.count(),
            'page': page,
            'limit': limit,
            'results': data
        }, status=status.HTTP_200_OK)


# ========================
# ❤️ Like/Unlike Project
# ========================
class LikeProjectView(APIView):
    """پروژه رو لایک/دیس‌لایک کن"""
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({
                'message': 'پروژه یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)

        # استفاده از domain service
        liked, total_likes = ProjectDomainService.toggle_like(project_id, request.user)

        # Log activity only if user liked (not unliked)
        if liked:
            from users.models import UserActivityLog
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='project_like',
                project=project,
                description=f'Liked project: {project.title}'
            )

        return Response({
            'liked': liked,
            'total_likes': total_likes,
            'message': 'لایک اضافه شد' if liked else 'لایک حذف شد'
        }, status=status.HTTP_200_OK)


# ========================
# 💬 Add Comment
# ========================
class ProjectCommentView(APIView):
    """کامنت اضافه کن یا لیست کامنت‌ها"""
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        """کامنت جدید اضافه کن"""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({
                'message': 'پروژه یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content', '').strip()
        if not content:
            return Response({
                'message': 'متن کامنت نمی‌تواند خالی باشد'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(content) > 1000:
            return Response({
                'message': 'کامنت نباید بیشتر از 1000 کاراکتر باشد'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = ProjectDomainService.add_comment(project_id, request.user, content)
            
            # Log activity
            from users.models import UserActivityLog
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='project_comment',
                project=project,
                description=f'Commented on project: {project.title}'
            )
            
            return Response({
                'message': 'کامنت اضافه شد',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': {
                        'id': comment.user.id,
                        'email': comment.user.email,
                        'name': comment.user.first_name or comment.user.username
                    },
                    'created_at': comment.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'message': f'خطا: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, project_id):
        """کامنت‌های پروژه را دریافت کن"""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({
                'message': 'پروژه یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)

        # پیجینگ
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        offset = (page - 1) * limit

        comments = project.comments.select_related('user').order_by('-created_at')[offset:offset + limit]

        data = []
        for comment in comments:
            data.append({
                'id': comment.id,
                'content': comment.content,
                'user': {
                    'id': comment.user.id,
                    'email': comment.user.email,
                    'name': comment.user.first_name or comment.user.username
                },
                'created_at': comment.created_at.isoformat()
            })

        return Response({
            'count': project.comments.count(),
            'page': page,
            'limit': limit,
            'results': data
        }, status=status.HTTP_200_OK)


# ========================
# 📥 Secure Download
# ========================
class SecureProjectDownloadView(APIView):
    """فایل پروژه رو دانلود کن"""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({
                'message': 'پروژه یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            file_path = project.file.path
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{slugify(project.title)}.{project.file.url.split(".")[-1]}"'
            return response
        except Exception as e:
            return Response({
                'message': f'خطا در دانلود: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# ========================
# 🔔 Notifications
# ========================
class NotificationListView(APIView):
    """اعلان‌های کاربر را دریافت کن"""
    permission_classes = []  # Allow for debugging, use IsAuthenticated in production

    def get(self, request):
        # اگر authenticated ہے تو اس کے notifications دکھاو
        if not request.user.is_authenticated:
            return Response({'results': [], 'count': 0}, status=status.HTTP_200_OK)
            
        # پیجینگ
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        offset = (page - 1) * limit

        # دریافت اعلان‌های کاربر (recipient_id = user)
        notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related('sender').order_by('-created_at')[offset:offset + limit]

        data = []
        for notif in notifications:
            data.append({
                'id': notif.id,
                'message': notif.message,
                'notification_type': notif.notification_type,
                'is_read': notif.is_read,
                'sender': {
                    'id': notif.sender.id if notif.sender else None,
                    'email': notif.sender.email if notif.sender else 'System',
                    'name': notif.sender.first_name or notif.sender.username if notif.sender else 'سیستم'
                } if notif.sender else None,
                'created_at': notif.created_at.isoformat()
            })

        return Response({
            'count': Notification.objects.filter(recipient=request.user).count(),
            'unread_count': Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count(),
            'page': page,
            'limit': limit,
            'results': data
        }, status=status.HTTP_200_OK)


class ClearNotificationView(APIView):
    """اعلان‌ها را حذف کن"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, notification_id=None):
        """
        اگر notification_id داده شد: یک اعلان حذف کن
        اگر notification_id نداده شد: تمام اعلان‌ها حذف کن
        """
        try:
            if notification_id:
                # یک اعلان حذف کن
                notification = Notification.objects.get(
                    id=notification_id,
                    recipient=request.user
                )
                notification.delete()
                return Response({
                    'message': 'اعلان حذف شد'
                }, status=status.HTTP_200_OK)
            else:
                # تمام اعلان‌ها حذف کن
                count, _ = Notification.objects.filter(
                    recipient=request.user
                ).delete()
                return Response({
                    'message': f'{count} اعلان حذف شد'
                }, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({
                'message': 'اعلان یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)


class MarkNotificationAsReadView(APIView):
    """اعلان رو خوانده شده علامت‌گذاری کن"""
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id=None):
        try:
            if notification_id:
                # یک اعلان خوانده شده علامت‌گذاری کن
                notification = Notification.objects.get(
                    id=notification_id,
                    recipient=request.user
                )
                notification.is_read = True
                notification.save()
                return Response({
                    'message': 'اعلان خوانده شده علامت‌گذاری شد'
                }, status=status.HTTP_200_OK)
            else:
                # تمام اعلان‌ها خوانده شده علامت‌گذاری کن
                Notification.objects.filter(
                    recipient=request.user,
                    is_read=False
                ).update(is_read=True)
                return Response({
                    'message': 'تمام اعلان‌ها خوانده شده علامت‌گذاری شدند'
                }, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({
                'message': 'اعلان یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)


# ========================
# 📊 Analytics
# ========================
class SystemAnalyticsView(APIView):
    """تحلیلات سیستم"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """اطلاعات تحلیلی سیستم"""
        # تعداد پروژه‌ها
        total_projects = Project.objects.count()
        user_projects = request.user.projects.count()

        # تعداد اعلان‌ها
        total_notifications = Notification.objects.filter(recipient=request.user).count()
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        # تعداد کاربران
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_users = User.objects.count()

        # فعالیت‌های اخیر (7 روز گذشته) - based on project uploads, likes, comments
        last_7_days = timezone.now() - timedelta(days=7)
        recent_activities = UserActivityLog.objects.filter(
            created_at__gte=last_7_days
        ).count()

        # پروژه‌های محبوب
        popular_projects = Project.objects.annotate(
            like_count=Count('likes')
        ).order_by('-like_count')[:5]

        popular_projects_data = []
        for project in popular_projects:
            popular_projects_data.append({
                'id': project.id,
                'title': project.title,
                'likes': project.like_count,
                'user': project.user.email
            })

        # کاربران فعال - based on UserActivityLog
        active_users = UserActivityLog.objects.values('user_id').annotate(
            activity_count=Count('id')
        ).order_by('-activity_count')[:5]

        active_users_data = []
        for activity in active_users:
            if activity['user_id']:
                user = User.objects.get(id=activity['user_id'])
                active_users_data.append({
                    'id': user.id,
                    'email': user.email,
                    'activities': activity['activity_count']
                })

        return Response({
            'summary': {
                'total_projects': total_projects,
                'user_projects': user_projects,
                'total_users': total_users,
                'total_notifications': total_notifications,
                'unread_notifications': unread_notifications,
                'recent_activities_7days': recent_activities
            },
            'popular_projects': popular_projects_data,
            'active_users': active_users_data
        }, status=status.HTTP_200_OK)


class UserAnalyticsView(APIView):
    """تحلیلات کاربر"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """تحلیلات شخصی کاربر"""
        user = request.user

        # پروژه‌های کاربر
        user_projects = user.projects.annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        )

        projects_data = []
        total_likes = 0
        total_comments = 0

        for project in user_projects:
            projects_data.append({
                'id': project.id,
                'title': project.title,
                'likes': project.like_count,
                'comments': project.comment_count,
                'created_at': project.created_at.isoformat()
            })
            total_likes += project.like_count
            total_comments += project.comment_count

        # فعالیت کاربر - project uploads, likes, comments
        user_uploads = UserActivityLog.objects.filter(
            user=user,
            activity_type='project_upload'
        ).count()
        
        user_likes = UserActivityLog.objects.filter(
            user=user,
            activity_type='project_like'
        ).count()
        
        user_comments_activity = UserActivityLog.objects.filter(
            user=user,
            activity_type='project_comment'
        ).count()

        # Recent activities
        recent_activities = UserActivityLog.objects.filter(
            user=user
        ).values('activity_type').annotate(count=Count('id'))

        activities_data = {}
        for act in recent_activities:
            activities_data[act['activity_type']] = act['count']

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username
            },
            'summary': {
                'total_projects': user_projects.count(),
                'total_likes_received': total_likes,
                'total_comments_received': total_comments,
            },
            'activities': {
                'project_uploads': user_uploads,
                'project_likes_given': user_likes,
                'project_comments_given': user_comments_activity,
            },
            'projects': projects_data,
            'activity_breakdown': activities_data
        }, status=status.HTTP_200_OK)



# ========================
# 🔍 Search
# ========================
class SearchView(APIView):
    """Full-text search across projects and users"""
    permission_classes = []  # Allow public search

    def get(self, request):
        """
        Search query: ?q=keyword&type=all|projects|users&limit=20
        """
        from projects.search import es_manager
        
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        limit = min(int(request.query_params.get('limit', 20)), 50)

        if not query or len(query) < 2:
            return Response({
                'message': 'Query must be at least 2 characters',
                'results': {'projects': [], 'users': [], 'total': 0}
            }, status=status.HTTP_400_BAD_REQUEST)

        if search_type == 'projects':
            results = {
                'projects': es_manager.search_projects(query, size=limit),
                'users': [],
                'total': len(es_manager.search_projects(query, size=limit))
            }
        elif search_type == 'users':
            results = {
                'projects': [],
                'users': es_manager.search_users(query, size=limit),
                'total': len(es_manager.search_users(query, size=limit))
            }
        else:  # all
            results = es_manager.search_all(query, size=limit)

        return Response(results, status=status.HTTP_200_OK)


class ReindexView(APIView):
    """Reindex all projects and users (admin only)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Trigger full reindex"""
        from projects.search import es_manager
        
        # Check if user is staff
        if not request.user.is_staff:
            return Response(
                {'message': 'Only staff can reindex'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        success = es_manager.reindex_all()
        
        if success:
            return Response({
                'message': 'Reindexing started successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Reindexing failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
