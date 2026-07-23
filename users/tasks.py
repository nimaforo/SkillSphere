# users/tasks.py
"""
🎯 Celery Tasks برای User Management
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

from users.models import Notification, UserActivityLog

User = get_user_model()
logger = logging.getLogger(__name__)

# ========================
# 📧 User Email Tasks
# ========================

@shared_task
def send_welcome_email(user_id):
    """
    نیے صارف کو welcome email بھیجیں
    
    Args:
        user_id: New User ID
    """
    try:
        user = User.objects.get(id=user_id)
        
        subject = "خوش آمدید! 👋 - SkillSphere"
        
        message = f"""
سلام {user.first_name or user.username}،

SkillSphere میں آپ کا خیر مقدم ہے! 🎉

ہم بہت خوش ہیں کہ آپ ہمارے کمیونٹی کا حصہ ہیں۔

شروع کرنے کے لیے:
1. اپنے پروفائل کو مکمل کریں
2. اپنا پہلا پروژہ شیئر کریں
3. دوسرے کے پروژے دیکھیں اور رائے دیں

اگر کوئی سوال ہو تو ہم سے رابطہ کریں۔

خوش رہیں!
SkillSphere ٹیم
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@skillsphere.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"✅ Welcome email sent to {user.email}")
        return f"Welcome email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return "User not found"
    except Exception as e:
        logger.error(f"❌ Error sending welcome email: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def send_password_reset_email(user_id, reset_token):
    """
    پاس ورڈ ری‌سیٹ ای‌میل بھیجیں
    
    Args:
        user_id: User ID
        reset_token: ری‌سیٹ ٹوکن
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Reset link
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        
        subject = "پاس ورڈ ری‌سیٹ کریں - SkillSphere"
        
        message = f"""
سلام {user.first_name or user.username}،

آپ نے اپنا پاس ورڈ ری‌سیٹ کرنے کی درخواست کی ہے۔

یہاں کلک کریں: {reset_url}

یہ لنک 24 گھنٹے میں ختم ہو جائے گا۔

اگر یہ آپ نے نہیں کیا تو اس ای‌میل کو نظر انداز کریں۔

SkillSphere ٹیم
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@skillsphere.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"✅ Password reset email sent to {user.email}")
        return f"Password reset email sent"
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return "User not found"
    except Exception as e:
        logger.error(f"❌ Error sending reset email: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def send_weekly_digest(user_id):
    """
    ہفتہ وار خلاصہ ای‌میل (نئے پروژے، تبصرے وغیرہ)
    
    Args:
        user_id: User ID
    """
    try:
        from projects.models import Project, ProjectComment
        from django.db.models import Count
        
        user = User.objects.get(id=user_id)
        
        # آخری 7 دن میں نئے پروژے
        last_week = timezone.now() - timedelta(days=7)
        new_projects = Project.objects.filter(created_at__gte=last_week).count()
        
        # صارف کے پروژوں پر تبصرے
        user_comments = ProjectComment.objects.filter(
            project__user=user,
            created_at__gte=last_week
        ).count()
        
        # صارف کے پروژوں پر لائکس (تقریباً)
        user_likes = sum([
            p.likes.filter(id__gte=timezone.now() - timedelta(days=7)).count()
            for p in user.projects.all()
        ])
        
        subject = f"📊 SkillSphere ہفتہ وار خلاصہ - {timezone.now().strftime('%Y-%m-%d')}"
        
        message = f"""
سلام {user.first_name or user.username}،

یہاں اس ہفتہ کا خلاصہ ہے:

📈 کمیونٹی کی سرگرمی:
   - نئے پروژے: {new_projects}
   - آپ کے پروژوں پر تبصرے: {user_comments}
   - آپ کے پروژوں پر لائکس: {user_likes}

اپنے ڈیش بورڈ پر مزید تفصیلات دیکھیں۔

ہفتہ وار رپورٹ
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@skillsphere.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"✅ Weekly digest sent to {user.email}")
        return f"Weekly digest sent"
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return "User not found"
    except Exception as e:
        logger.error(f"❌ Error sending digest: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# 📊 User Statistics
# ========================

@shared_task
def calculate_user_statistics(user_id):
    """
    صارف کے اعدادوشمار کا حساب لگائیں
    
    Args:
        user_id: User ID
    """
    try:
        from projects.models import Project
        from django.db.models import Count
        
        user = User.objects.get(id=user_id)
        
        stats = {
            'projects_count': user.projects.count(),
            'total_likes': sum([p.likes.count() for p in user.projects.all()]),
            'total_comments': sum([p.comments.count() for p in user.projects.all()]),
            'notifications': Notification.objects.filter(recipient=user).count(),
            'unread_notifications': Notification.objects.filter(
                recipient=user,
                is_read=False
            ).count(),
        }
        
        logger.info(f"✅ Statistics calculated for user {user_id}: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error calculating statistics: {str(e)}")
        return f"Error: {str(e)}"


# ========================
# 🔄 Account Management
# ========================

@shared_task
def deactivate_inactive_accounts(days=90):
    """
    غیر فعال اکاؤنٹ کو غیر فعال کریں
    
    Args:
        days: کتنے دن سے غیر فعال (default: 90)
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # آخری log check
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True
        )
        
        deactivated_count = 0
        for user in inactive_users:
            user.is_active = False
            user.save()
            deactivated_count += 1
            
            # انہیں مطلع کریں
            send_mail(
                subject="اکاؤنٹ غیر فعال - SkillSphere",
                message=f"آپ کا اکاؤنٹ غیر فعال کر دیا گیا ہے کیونکہ آپ {days} دن سے لاگ ان نہیں کیے۔",
                from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@skillsphere.com',
                recipient_list=[user.email],
                fail_silently=True,
            )
        
        logger.info(f"✅ Deactivated {deactivated_count} inactive accounts")
        return f"Deactivated {deactivated_count} accounts"
        
    except Exception as e:
        logger.error(f"❌ Error deactivating accounts: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def delete_pending_accounts(days=7):
    """
    زیادہ دیر سے pending اکاؤنٹ کو حذف کریں
    
    Args:
        days: کتنے دن pending (default: 7)
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Pending users (مثلاً is_active=False)
        pending_users = User.objects.filter(
            is_active=False,
            date_joined__lt=cutoff_date
        )
        
        deleted_count = pending_users.count()
        pending_users.delete()
        
        logger.info(f"✅ Deleted {deleted_count} pending accounts")
        return f"Deleted {deleted_count} accounts"
        
    except Exception as e:
        logger.error(f"❌ Error deleting pending accounts: {str(e)}")
        return f"Error: {str(e)}"
