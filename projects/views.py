# projects/views.py
import os
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from users.models import Notification
from .models import Project, ProjectComment
from .throttles import UploadBurstThrottle, ActionBurstThrottle  
from .domain.services import ProjectDomainService

User = get_user_model()


# ==========================================
# ۱. کلاس آپلود فایل پروژه (محدود شده با Rate Limiting)
# ==========================================
class ProjectFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [UploadBurstThrottle]  # حداکثر ۵ آپلود در دقیقه

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        uploaded_file = request.data.get('file')

        if not uploaded_file:
            return Response({"message": "هیچ فایلی ارسال نشده است!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.create(
                user=request.user,
                title=title,
                description=description,
                file=uploaded_file
            )

            return Response({
                "project_id": project.id,
                "file_url": project.file.url,
                "message": "فایل با موفقیت در سرور داکر ذخیره شد."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"message": f"خطای سرور: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# ۲. کلاس ویترین و فید پروژه‌ها
# ==========================================
class ProjectFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.all().order_by('-created_at')
        data = []
        for p in projects:
            comments = [
                {
                    "id": comment.id,
                    "user": comment.user.email,
                    "text": comment.content,
                    "created_at": comment.created_at.isoformat(),
                }
                for comment in p.comments.all()
            ]
            data.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "file_url": p.file.url if p.file else "",
                "uploader": p.user.email,
                "likes_count": p.total_likes(),
                "is_liked": request.user in p.likes.all(),
                "comments": comments,
            })
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        title = request.data.get('title', '').strip()
        description = request.data.get('description', '').strip()

        if not title:
            return Response({'message': 'عنوان پروژه الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.create(
            user=request.user,
            title=title,
            description=description,
            file=request.FILES.get('file') if 'file' in request.FILES else None,
        )

        return Response(
            {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'uploader': project.user.email,
                'file_url': project.file.url if project.file else '',
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================
# ۳. جزییات و قابلیت حذف پروژه توسط مالک پروژه
# ==========================================
class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            
            if project.user != request.user:
                return Response({"message": "شما اجازه حذف این پروژه را ندارید."}, status=status.HTTP_403_FORBIDDEN)
            
            if project.file:
                if default_storage.exists(project.file.name):
                    default_storage.delete(project.file.name)
            
            project.delete()
            return Response({"message": "پروژه با موفقیت حذف شد."}, status=status.HTTP_200_OK)
            
        except Project.DoesNotExist:
            return Response({"message": "پروژه یافت نشد"}, status=status.HTTP_404_NOT_FOUND)


# ==========================================
# ۴. مدیریت لایک با هدایت به لایه دامین (Hexagonal / DDD)
# ==========================================
class LikeProjectView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ActionBurstThrottle]  # حداکثر ۳۰ لایک در دقیقه

    def post(self, request, project_id):
        try:
            # واگذاری منطق بیزینس، وب‌سوکت چنلز و اعلانات دیتابیس به لایه دامین
            liked, likes_count = ProjectDomainService.toggle_like(
                project_id=project_id,
                user=request.user
            )
            return Response({"liked": liked, "likes_count": likes_count}, status=status.HTTP_200_OK)
            
        except Project.DoesNotExist:
            return Response({"message": "پروژه یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"خطای سرور: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# ۵. مدیریت کامنت با هدایت به لایه دامین (Hexagonal / DDD)
# ==========================================
class ProjectCommentView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ActionBurstThrottle]  # حداکثر ۳۰ کامنت در دقیقه

    def post(self, request, project_id):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"message": "متن کامنت نمی‌تواند خالی باشد."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # واگذاری ثبت کامنت و مدیریت زنجیره اعلانات به لایه دامین
            comment = ProjectDomainService.add_comment(
                project_id=project_id,
                user=request.user,
                text=text
            )
            return Response(
                {
                    "id": comment.id,
                    "user": comment.user.email,
                    "text": comment.content,
                    "created_at": comment.created_at.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        except Project.DoesNotExist:
            return Response({"message": "پروژه یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"خطای سرور: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# ۶. حذف و پاک‌سازی اعلان‌ها (رفع ارور وابستگی نامعلوم)
# ==========================================
class ClearNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        """حذف یک اعلان مشخص براساس آیدی آن"""
        try:
            try:
                notification = Notification.objects.get(id=notification_id, user=request.user)
            except Exception:  
                notification = Notification.objects.get(id=notification_id, recipient=request.user)
                
            notification.delete()
            return Response({"message": "اعلان با موفقیت حذف شد."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "اعلان یافت نشد یا دسترسی مجاز نیست."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """حذف یکجای تمام اعلان‌های کاربر جاری"""
        try:
            Notification.objects.filter(user=request.user).delete()
        except Exception:
            Notification.objects.filter(recipient=request.user).delete()
            
        return Response({"message": "تمام اعلان‌ها با موفقیت پاک‌سازی شدند."}, status=status.HTTP_200_OK)


# ==========================================
# ۷. دانلود امن و کنترل‌شده فایل‌ها از داکر استوریج
# ==========================================
class SecureProjectDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            
            if not project.file:
                return Response({"message": "فایلی برای این پروژه آپلود نشده است."}, status=status.HTTP_404_NOT_FOUND)
            
            if not project.file.storage.exists(project.file.name):
                return Response({"message": "فایل فیزیکی روی استوریج سرور یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

            project_file = project.file.open(mode='rb')
            response = FileResponse(project_file, content_type='application/octet-stream')
            
            file_name = os.path.basename(project.file.name)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            
            return response

        except Project.DoesNotExist:
            return Response({"message": "پروژه یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"❌ Error in Secure Download API: {str(e)}")
            return Response({"message": f"خطای سرور: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# ۸. تحلیل و آمار کلیدی کل سیستم
# ==========================================
class SystemAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            total_projects = Project.objects.count()
            total_users = User.objects.count()
            total_comments = ProjectComment.objects.count()

            most_liked_project = Project.objects.annotate(
                num_likes=Count('likes')
            ).order_by('-num_likes').first()

            popular_project_data = None
            if most_liked_project:
                popular_project_data = {
                    "id": most_liked_project.id,
                    "title": most_liked_project.title,
                    "likes": most_liked_project.num_likes,
                    "uploader": most_liked_project.user.email
                }

            try:
                top_uploaders = User.objects.annotate(
                    project_count=Count('projects')
                ).order_by('-project_count')[:3]
                uploaders_data = [{"email": u.email, "count": u.project_count} for u in top_uploaders]
            except Exception:
                top_uploaders = User.objects.annotate(
                    project_count=Count('project')
                ).order_by('-project_count')[:3]
                uploaders_data = [{"email": u.email, "count": u.project_count} for u in top_uploaders]

            analytics_data = {
                "summary": {
                    "total_projects": total_projects,
                    "total_users": total_users,
                    "total_comments": total_comments,
                },
                "popular_project": popular_project_data,
                "top_uploaders": uploaders_data
            }

            return Response(analytics_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": f"خطا در واکشی آمار سیستم: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )