# projects/middleware.py
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    """
    توکن JWT را رمزگشایی کرده و کاربر را از دیتابیس بازیابی می‌کند
    """
    try:
        if not token_key:
            return None
            
        # رمزگشایی توکن JWT
        token = AccessToken(token_key)
        user_id = token.get('user_id')
        
        if user_id:
            user = User.objects.get(id=user_id)
            return user
        return None
    except TokenError as e:
        print(f"❌ خطای توکن JWT: {str(e)}")
        return None
    except User.DoesNotExist:
        print(f"❌ کاربر با این ID یافت نشد")
        return None
    except Exception as e:
        print(f"❌ خطای نامشخص در JWT middleware: {str(e)}")
        return None

class JwtAuthMiddleware:
    """
    میدل‌ور اختصاصی برای استخراج توکن JWT از WebSocket URL و احراز هویت کاربر
    
    استفاده:
    - ws://localhost:8000/ws/notifications/?token=YOUR_JWT_TOKEN
    - ws://localhost:8000/ws/chat/1/?token=YOUR_JWT_TOKEN
    """
    
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # استخراج Query String از WebSocket URL
        query_string = scope.get("query_string", b"").decode("utf-8")
        path = scope.get("path", "")
        print(f"\n🔍 JwtAuthMiddleware - Path: {path}")
        print(f"🔍 Query String: {query_string[:100] if query_string else 'EMPTY'}")
        
        # Parse query string برای استخراج توکن
        token = None
        if query_string:
            try:
                # استفاده از parse_qs برای parsing صحیح
                query_params = parse_qs(query_string)
                token_list = query_params.get('token', [])
                token = token_list[0] if token_list else None
                if token:
                    print(f"✅ Token found: {token[:30]}...")
                else:
                    print(f"❌ No token in query params. Keys: {list(query_params.keys())}")
            except Exception as e:
                print(f"⚠️ خطا در parsing query string: {e}")

        # احراز هویت کاربر
        if token:
            user = await get_user_from_token(token)
            if user:
                scope['user'] = user
                print(f"✅ کاربر {user.email} موفقاً احراز هویت شد")
            else:
                scope['user'] = AnonymousUser()
                print(f"⚠️ توکن نامعتبر: احراز هویت ناموفق")
        else:
            scope['user'] = AnonymousUser()
            print(f"⚠️ توکن یافت نشد در query string")

        # ارسال scope به درون middleware
        return await self.inner(scope, receive, send)