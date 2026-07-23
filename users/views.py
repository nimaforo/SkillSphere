# C:/Users/nimaf/web project/webproject/users/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name', '')

            if not email or not password:
                return JsonResponse({'message': 'ایمیل و رمز عبور الزامی هستند.'}, status=400)

            if User.objects.filter(username=email).exists():
                return JsonResponse({'message': 'این ایمیل قبلاً ثبت‌نام شده است.'}, status=400)

            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=password,
                first_name=name
            )
            user.save()
            return JsonResponse({'message': 'ثبت‌نام با موفقیت انجام شد!'}, status=201)

        except Exception as e:
            return JsonResponse({'message': f'خطای سرور: {str(e)}'}, status=500)
            
    return JsonResponse({'message': 'متد نامعتبر است.'}, status=405)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'detail': 'لطفاً ایمیل و رمز عبور را وارد کنید.'}, status=400)

            # تایید هویت کاربر روی مدل سفارشی دیتابیس داکر
            user = authenticate(username=username, password=password)

            if user is not None:
                # 🔥 ساخت توکن واقعی و معتبر JWT 🔥
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'message': 'خوش آمدید!'
                }, status=200)
            else:
                return JsonResponse({'detail': 'ایمیل یا رمز عبور اشتباه است!'}, status=401)

        except Exception as e:
            return JsonResponse({'detail': f'خطای سرور: {str(e)}'}, status=500)

    return JsonResponse({'detail': 'متد نامعتبر است.'}, status=405)


# ========================
# 👤 User Profile
# ========================
class UserProfileView(APIView):
    """Get detailed user profile with stats"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from projects.models import Project, ProjectComment
        from users.models import UserActivityLog

        # User's projects
        user_projects = user.projects.all()
        total_projects = user_projects.count()
        
        # Total likes and comments on user's projects
        total_likes = sum(p.total_likes() for p in user_projects)
        total_comments = ProjectComment.objects.filter(project__user=user).count()
        
        # User activity (7 days) - from UserActivityLog
        last_7_days = timezone.now() - timedelta(days=7)
        recent_activity = UserActivityLog.objects.filter(
            user=user,
            created_at__gte=last_7_days
        ).count()
        
        # User's comments on others' projects
        user_comments = ProjectComment.objects.filter(user=user).count()
        
        # Recent projects
        recent_projects = user_projects.order_by('-created_at')[:5]
        recent_projects_data = []
        for project in recent_projects:
            recent_projects_data.append({
                'id': project.id,
                'title': project.title,
                'likes': project.total_likes(),
                'comments': project.comments.count(),
                'created_at': project.created_at.isoformat()
            })

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'username': user.username,
                'date_joined': user.date_joined.isoformat()
            },
            'stats': {
                'total_projects': total_projects,
                'total_likes_received': total_likes,
                'total_comments_on_projects': total_comments,
                'total_comments_made': user_comments,
                'recent_activity_7days': recent_activity,
            },
            'recent_projects': recent_projects_data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        """Update user profile"""
        user = request.user
        name = request.data.get('first_name')
        
        if name:
            user.first_name = name
            user.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name
                }
            }, status=status.HTTP_200_OK)
        
        return Response({'message': 'No changes'}, status=status.HTTP_400_BAD_REQUEST)
