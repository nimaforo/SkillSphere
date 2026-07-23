# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'chat_{self.project_id}'

        # Check authentication
        if not self.scope.get('user') or self.scope['user'].is_anonymous:
            print(f"❌ Chat: Anonymous user attempted to connect to chat/{self.project_id}")
            await self.close()
            return

        print(f"✅ Chat: User {self.scope['user']} connected to chat/{self.project_id}")

        # ورود به اتاق چت اختصاصی این پروژه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # خروج از اتاق چت
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

  # دریافت پیام از مرورگر کاربر
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope["user"].username if self.scope["user"].is_authenticated else "کاربر ناشناس"

        # حتماً باید این خط await داشته باشد تا پیام را به ردیس بفرستد
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # دریافت پیام از اتاق و چاپ آن برای کاربر
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # ارسال نهایی پیام به مرورگر از طریق وب‌ساکت (این خط هم باید await داشته باشد)
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))