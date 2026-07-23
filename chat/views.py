import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # برای اینکه فرانت‌اند بدون خطای CSRF بتونه دیتا بفرسته
def register_view(request):
    if request.method == 'POST':
        try:
            # خواندن دیتای JSON فرستاده شده از ری‌آکت
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name', '')

            if not email or not password:
                return JsonResponse({'message': 'ایمیل و رمز عبور الزامی هستند.'}, status=400)

            # بررسی تکراری نبودن کاربر
            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'این ایمیل قبلاً ثبت‌نام شده است.'}, status=400)

            # ساخت کاربر جدید در دیتابیس داکر
            # از ایمیل به عنوان یوزرنیم استفاده می‌کنیم تا تداخل ایجاد نشود
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=password,
                first_name=name
            )
            user.save()

            return JsonResponse({'message': 'ثبت‌نام با موفقیت انجام شد!'}, status=201)

        except Exception as e:
            # اگر خطای ۵۰۰ رخ داد، این خط خطا رو در لاگ داکر چاپ میکنه تا ببینیم چیه
            print("Registration Error:", str(e))
            return JsonResponse({'message': f'خطای سرور: {str(e)}'}, status=500)
            
    return JsonResponse({'message': 'متد نامعتبر است.'}, status=405)