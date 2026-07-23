# projects/tasks.py
"""
🎯 Celery Tasks برای SkillSphere
تمام background jobs هنا تعریف میشوند
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile
import logging

from projects.models import Project, ProjectComment
from users.models import Notification, UserActivityLog

User = get_user_model()
logger = logging.getLogger(__name__)

# ========================
# 📧 Email Notifications
# ========================

@shared_task(bind=True, max_retries=3)
def send_notification_email(self, notification_id):
    """
    اعلان کاربر را از طریق ایمیل ارسال کن
    
    Args:
        notification_id: Notification ID
    
    Retries:
        اگر خطا داد، 3 بار دوباره تلاش کن
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        recipient_email = notification.recipient.email
        
        subject = f"🔔 اعلان جدید - SkillSphere"
        
        # ساختار ایمیل
        message = f"""
سلام {notification.recipient.first_name or notification.recipient.username}،

اعلان جدیدی برای شما وجود دارد:

📢 {notification.message}

نوع اعلان: {notification.get_notification_type_display()}

لطفاً به SkillSphere بروید تا جزئیات بیشتری ببینید.

تشکر،
تیم SkillSphere
        """
        
        # ارسال ایمیل
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@skillsphere.com',
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"✅ Email sent to {recipient_email} for notification {notification_id}")
        return f"Email sent successfully to {recipient_email}"
        
    except Notification.DoesNotExist:
        logger.error(f"❌ Notification {notification_id} not found")
        return f"Notification {notification_id} not found"
    except Exception as exc:
        logger.error(f"❌ Error sending email: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_bulk_notification_emails(user_ids=None, notification_type=None):
    """
    بصورت فی‌الوقت تمام اعلان‌های خوانده نشده کو ایمیل کن
    
    Args:
        user_ids: اختیاری - خاص users کو ایمیل کریں
        notification_type: اختیاری - صرف خاص نوع اعلان
    """
    try:
        # اعلان‌های خوانده نشده حاصل کریں
        query = Notification.objects.filter(is_read=False)
        
        if notification_type:
            query = query.filter(notification_type=notification_type)
        
        if user_ids:
            query = query.filter(recipient_id__in=user_ids)
        
        notifications = query[:100]  # حد سے زیادہ بھیجنے سے بچیں
        
        sent_count = 0
        for notification in notifications:
            send_notification_email.delay(notification.id)
            sent_count += 1
        
        logger.info(f"✅ Queued {sent_count} emails for sending")
        return f"Queued {sent_count} emails"
        
    except Exception as e:
        logger.error(f"❌ Error in bulk email: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# 🖼️ File Processing
# ========================

@shared_task(bind=True, max_retries=2)
def generate_project_thumbnail(self, project_id):
    """
    پروژہ کے لیے تھمبنیل تصویر بنائیں
    (اگر یہ ایک تصویر ہے)
    
    Args:
        project_id: Project ID
    """
    try:
        project = Project.objects.get(id=project_id)
        
        # صرف image files میں تھمبنیل بنائیں
        if not project.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            logger.info(f"⏭️ Project {project_id} is not an image, skipping thumbnail")
            return "Not an image file"
        
        # اصل تصویر کھولیں
        image = Image.open(project.file.path)
        
        # تھمبنیل سائز
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        
        # ایک BytesIO میں رکھیں
        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)
        
        # تھمبنیل کو نام دیں
        thumb_filename = f"thumbnails/{project.id}_thumb.jpg"
        
        # Django's default storage میں save کریں
        project.file_thumbnail = ContentFile(thumb_io.read(), name=thumb_filename)
        project.save(update_fields=['file_thumbnail'])
        
        logger.info(f"✅ Thumbnail generated for project {project_id}")
        return f"Thumbnail generated successfully"
        
    except Project.DoesNotExist:
        logger.error(f"❌ Project {project_id} not found")
        return f"Project not found"
    except Exception as exc:
        logger.error(f"❌ Error generating thumbnail: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def compress_project_file(project_id):
    """
    پروژہ فائل کو compress کریں
    (اگر یہ PDF یا دیگر format ہے)
    
    Args:
        project_id: Project ID
    """
    try:
        project = Project.objects.get(id=project_id)
        
        logger.info(f"🔄 Compression task queued for project {project_id}")
        logger.info(f"   File: {project.file.name}")
        logger.info(f"   Size: {project.file.size / (1024 * 1024):.2f} MB")
        
        # ملیٹک کے لیے compression logic یہاں ہے
        # فی الوقت - sirf log کریں
        
        return f"Compression initiated for project {project_id}"
        
    except Project.DoesNotExist:
        logger.error(f"❌ Project {project_id} not found")
        return "Project not found"
    except Exception as e:
        logger.error(f"❌ Error compressing file: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# 📊 Analytics & Reports
# ========================

@shared_task
def generate_user_analytics_report(user_id):
    """
    کاربر کے لیے تجزیاتی رپورٹ بنائیں
    
    Args:
        user_id: User ID
    """
    try:
        user = User.objects.get(id=user_id)
        
        # تحلیلات حاصل کریں
        user_projects = user.projects.count()
        total_likes = sum([p.likes.count() for p in user.projects.all()])
        total_comments = sum([p.comments.count() for p in user.projects.all()])
        notifications_received = Notification.objects.filter(recipient=user).count()
        
        report = {
            'user_email': user.email,
            'total_projects': user_projects,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'notifications': notifications_received,
            'generated_at': str(timezone.now())
        }
        
        logger.info(f"✅ Analytics report generated for user {user_id}: {report}")
        return report
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return "User not found"
    except Exception as e:
        logger.error(f"❌ Error generating report: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def generate_system_analytics_report():
    """
    پوری سسٹم کے لیے تجزیاتی رپورٹ بنائیں
    """
    try:
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # سسٹم stats
        total_users = User.objects.count()
        total_projects = Project.objects.count()
        total_comments = ProjectComment.objects.count()
        total_notifications = Notification.objects.count()
        
        # آخری 7 دن کی سرگرمی
        last_7_days = timezone.now() - timedelta(days=7)
        recent_projects = Project.objects.filter(created_at__gte=last_7_days).count()
        recent_comments = ProjectComment.objects.filter(created_at__gte=last_7_days).count()
        
        # محبوب پروژے
        popular_projects = Project.objects.annotate(
            like_count=Count('likes')
        ).order_by('-like_count')[:5]
        
        # فعال صارفین
        active_users = User.objects.annotate(
            project_count=Count('projects')
        ).filter(project_count__gt=0).count()
        
        report = {
            'total_users': total_users,
            'total_projects': total_projects,
            'total_comments': total_comments,
            'total_notifications': total_notifications,
            'recent_projects_7days': recent_projects,
            'recent_comments_7days': recent_comments,
            'active_users': active_users,
            'popular_projects_count': popular_projects.count(),
            'generated_at': str(timezone.now())
        }
        
        logger.info(f"✅ System analytics report generated: {report}")
        return report
        
    except Exception as e:
        logger.error(f"❌ Error generating system report: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# 🧹 Cleanup Tasks
# ========================

@shared_task
def cleanup_old_notifications(days=30):
    """
    پرانے اعلان کو حذف کریں
    
    Args:
        days: کتنے دن پہلے سے پرانے حذف کریں (default: 30)
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()
        
        logger.info(f"✅ Deleted {deleted_count} old notifications (before {cutoff_date})")
        return f"Deleted {deleted_count} notifications"
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up notifications: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_orphaned_files():
    """
    اضافی files کو حذف کریں جن کے لیے project نہیں ہے
    """
    try:
        import os
        from django.conf import settings
        
        media_path = settings.MEDIA_ROOT
        project_files_path = os.path.join(media_path, 'project_files')
        
        if not os.path.exists(project_files_path):
            return "Project files directory not found"
        
        # تمام files حاصل کریں
        all_files = set(os.listdir(project_files_path))
        
        # تمام projects میں استعمال ہونے والی files
        used_files = set()
        for project in Project.objects.all():
            if project.file:
                used_files.add(os.path.basename(project.file.name))
        
        # اضافی files
        orphaned_files = all_files - used_files
        
        deleted_count = 0
        for filename in orphaned_files:
            try:
                file_path = os.path.join(project_files_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Could not delete {filename}: {str(e)}")
        
        logger.info(f"✅ Deleted {deleted_count} orphaned files")
        return f"Deleted {deleted_count} orphaned files"
        
    except Exception as e:
        logger.error(f"❌ Error in cleanup: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# 🔔 Activity Logging
# ========================

@shared_task
def log_user_activity(user_id, path, method, status_code, duration, ip_address=None):
    """
    کاربر کی سرگرمی کو log کریں
    (یہ عام طور پر middleware سے called ہوتا ہے)
    
    Args:
        user_id: User ID
        path: API path
        method: HTTP method
        status_code: Response status
        duration: Request duration
        ip_address: User's IP
    """
    try:
        user = User.objects.get(id=user_id) if user_id else None
        
        UserActivityLog.objects.create(
            user=user,
            path=path,
            method=method,
            status_code=status_code,
            duration=duration,
            ip_address=ip_address
        )
        
        return f"Activity logged for user {user_id}"
        
    except Exception as e:
        logger.error(f"❌ Error logging activity: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# ⏱️ Periodic Tasks (Beat)
# ========================

@shared_task
def daily_tasks():
    """
    روزانہ کی سرگرمیاں جو scheduled ہوں
    """
    try:
        logger.info("🕐 Running daily tasks...")
        
        # تحلیلات report
        generate_system_analytics_report.delay()
        
        # صاف ستھرائی
        cleanup_old_notifications.delay(days=30)
        cleanup_orphaned_files.delay()
        
        logger.info("✅ Daily tasks completed")
        return "Daily tasks completed"
        
    except Exception as e:
        logger.error(f"❌ Error in daily tasks: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def weekly_tasks():
    """
    ہفتہ وار کی سرگرمیاں
    """
    try:
        logger.info("📅 Running weekly tasks...")
        
        # تمام users کے لیے analytics
        users = User.objects.all()
        for user in users:
            generate_user_analytics_report.delay(user.id)
        
        logger.info(f"✅ Weekly tasks completed for {users.count()} users")
        return f"Weekly tasks completed"
        
    except Exception as e:
        logger.error(f"❌ Error in weekly tasks: {str(e)}")
        return f"Error: {str(e)}"
