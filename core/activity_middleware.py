# core/activity_middleware.py
import time
from django.db import connection
from django.db.utils import ProgrammingError

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # زمان شروع درخواست
        start_time = time.time()

        # ارجاع درخواست به ویو و دریافت پاسخ
        response = self.get_response(request)

        # محاسبه مدت زمان پردازش
        duration = time.time() - start_time

        # استخراج IP کاربر
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # ذخیره لاگ در دیتابیس (فقط برای مسیرهای API تا دیتابیس شلوغ نشود)
        if request.path.startswith('/api/'):
            try:
                from users.models import UserActivityLog
                UserActivityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    path=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    duration=round(duration, 4),
                    ip_address=ip
                )
            except (ProgrammingError, Exception) as e:
                # Table might not exist yet - safely ignore
                pass

        return response