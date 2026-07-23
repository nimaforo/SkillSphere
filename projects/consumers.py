import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer برای چت اختصاصی پروژه‌ها
    URL: ws://localhost:8000/ws/chat/<project_id>/?token=YOUR_JWT_TOKEN
    """
    
    async def connect(self):
        # Initialize before any early returns
        self.room_group_name = None
        self.user = self.scope['user']
        
        print(f"🔍 ChatConsumer connect() called. User: {self.user}, Is Anonymous: {isinstance(self.user, AnonymousUser)}")
        
        # بررسی authentication
        if isinstance(self.scope['user'], AnonymousUser):
            print("❌ ChatConsumer: کاربر احراز هویت نشده است")
            await self.close()
            return

        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'chat_{self.project_id}'

        print(f"✅ کاربر {self.user.email} به چت پروژه {self.project_id} متصل شد")

        # عضویت در گروه چت اختصاصی این پروژه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # قبول کردن اتصال وب‌سوکت
        await self.accept()

    async def disconnect(self, close_code):
        # خروج از گروه هنگام قطع اتصال (safely check if group was set)
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"🔌 کاربر {self.user.email} از چت پروژه {self.project_id} قطع شد")

    async def receive(self, text_data):
        """دریافت پیام از فرانت‌آند"""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '').strip()
            
            if not message:
                await self.send(text_data=json.dumps({
                    'error': 'پیام نمی‌تواند خالی باشد'
                }))
                return

            # انتشار پیام دریافت شده به تمام اعضای این اتاق چت
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.email,
                    'sender_id': self.user.id,
                    'project_id': self.project_id
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'JSON نامعتبر'
            }))
        except Exception as e:
            print(f"❌ خطا در receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': f'خطا: {str(e)}'
            }))

    async def chat_message(self, event):
        """متد کمکی برای ارسال پیام به کلاینت‌ها"""
        message = event['message']
        sender = event['sender']
        sender_id = event['sender_id']

        # ارسال فیزیکی دیتا روی وب‌سوکت به فرانت‌آند
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'sender_id': sender_id,
            'project_id': event['project_id']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer برای اعلان‌های real-time اختصاصی کاربر
    URL: ws://localhost:8000/ws/notifications/?token=YOUR_JWT_TOKEN
    
    فقط اعلان‌های مربوط به کاربر احراز هویت شده ارسال می‌شود
    """
    
    async def connect(self):
        # Initialize before any early returns
        self.user = self.scope['user']
        self.user_notification_group = None
        
        # بررسی authentication (حتمی است)
        if isinstance(self.scope['user'], AnonymousUser):
            print("❌ NotificationConsumer: کاربر احراز هویت نشده است")
            await self.close()
            return

        # هر کاربر یک اتاق notification اختصاصی دارد
        self.user_notification_group = f'notifications_user_{self.user.id}'

        print(f"✅ کاربر {self.user.email} به سیستم اعلان‌ها متصل شد")

        # عضویت در گروه اعلان اختصاصی این کاربر
        await self.channel_layer.group_add(
            self.user_notification_group,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # خروج از گروه هنگام قطع اتصال (safely check if group was set)
        if self.user_notification_group:
            await self.channel_layer.group_discard(
                self.user_notification_group,
                self.channel_name
            )
            print(f"🔌 کاربر {self.user.email} از سیستم اعلان‌ها قطع شد")

    async def send_notification(self, event):
        """
        متد کمکی برای ارسال اعلان‌ها
        event dict شامل: notification_type, message, project_id, user_id
        """
        notification_type = event.get("notification_type", "INFO")
        message = event.get("message", "")
        project_id = event.get("project_id")
        sender_id = event.get("sender_id")
        
        # تنها اگر اعلان برای این کاربر باشد ارسال کن
        if event.get("user_id") == self.user.id:
            print(f"📢 اعلان برای کاربر {self.user.email}: {message}")
            
            await self.send(text_data=json.dumps({
                "type": notification_type,
                "message": message,
                "project_id": project_id,
                "sender_id": sender_id,
                "timestamp": event.get("timestamp", "")
            }))
        else:
            # اگر اعلان برای کاربر دیگری است، نادیده بگیر
            pass