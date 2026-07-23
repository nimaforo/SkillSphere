# projects/domain/services.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from projects.models import Project, ProjectComment
from users.models import Notification
from datetime import datetime

class ProjectDomainService:
    """
    هسته اصلی منطق بیزینس پروژه SkillSphere.
    این کلاس هیچ وابستگی مستقیمی به API Viewهای جنگو ندارد.
    """

    @staticmethod
    def toggle_like(project_id, user) -> tuple[bool, int]:
        """منطق بیزینس لایک و دیس‌لایک به همراه شلیک اعلان ریل‌تایم"""
        project = Project.objects.get(id=project_id)
        
        if user in project.likes.all():
            project.likes.remove(user)
            liked = False
        else:
            project.likes.add(user)
            liked = True
            
            # ارسال نوتیفیکیشن فقط در صورتی که لایک کننده خود مالک نباشد
            if project.user != user:
                ProjectDomainService._dispatch_notifications(
                    recipient_user=project.user,
                    trigger_user=user,
                    notif_type="like",
                    ws_message=f"پروژه «{project.title}» توسط {user.email} لایک شد! ❤️",
                    db_message=f"{user.email} پروژه شما را لایک کرد.",
                    project_id=project.id,
                    sender_id=user.id
                )
                
        return liked, project.total_likes()

    @staticmethod
    def add_comment(project_id, user, text: str):
        """منطق بیزینس ثبت کامنت به همراه شلیک اعلان ریل‌تایم"""
        project = Project.objects.get(id=project_id)
        comment = ProjectComment.objects.create(project=project, user=user, content=text)
        
        if project.user != user:
            ProjectDomainService._dispatch_notifications(
                recipient_user=project.user,
                trigger_user=user,
                notif_type="chat",
                ws_message=f"{user.email} روی پروژه «{project.title}» کامنت گذاشت. 💬",
                db_message=f"{user.email} روی پروژه شما کامنت گذاشت.",
                project_id=project.id,
                sender_id=user.id
            )
            
        return comment

    @staticmethod
    def _dispatch_notifications(
        recipient_user, 
        trigger_user, 
        notif_type: str, 
        ws_message: str, 
        db_message: str,
        project_id: int,
        sender_id: int
    ):
        """
        متد کمکی داخلی لایه دامین برای مدیریت موازی وب‌سوکت و دیتابیس
        
        Args:
            recipient_user: کاربری که باید اعلان دریافت کند
            trigger_user: کاربری که عملیات را انجام داد
            notif_type: نوع اعلان (like, chat, system)
            ws_message: پیام برای WebSocket (realtime)
            db_message: پیام برای دیتابیس (persistence)
            project_id: شناسه پروژه
            sender_id: شناسه کاربری که عملیات را انجام داد
        """
        
        # ۱. لایه وب‌سوکت چنلز (ریل‌تایم) - ارسال فقط برای کاربر مقصد
        try:
            channel_layer = get_channel_layer()
            user_notification_group = f'notifications_user_{recipient_user.id}'
            
            async_to_sync(channel_layer.group_send)(
                user_notification_group,
                {
                    "type": "send_notification",
                    "notification_type": notif_type.upper(),
                    "message": ws_message,
                    "project_id": project_id,
                    "user_id": recipient_user.id,  # اعلان فقط برای این کاربر
                    "sender_id": sender_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ اعلان WebSocket برای کاربر {recipient_user.email} ارسال شد")
        except Exception as ws_err:
            print(f"⚠️ [Domain] خطا در ارسال وب‌سوکت: {ws_err}")

        # ۲. لایه ذخیره‌سازی دیتابیس
        try:
            Notification.objects.create(
                recipient=recipient_user,  # تصحیح: recipient به جای user
                sender=trigger_user,        # اضافه کردن sender
                message=db_message,
                notification_type=notif_type
            )
            print(f"✅ اعلان دیتابیس برای کاربر {recipient_user.email} ذخیره شد")
        except Exception as db_err:
            print(f"⚠️ [Domain] خطای ذخیره دیتابیس اعلان: {db_err}")