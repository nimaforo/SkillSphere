# users/adapters/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from users.adapters.serializers import UserRegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "ثبت‌نام با موفقیت انجام شد."}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ویوی لاگین سفارشی شده با استفاده از SimpleJWT که بر پایه ایمیل کار خواهد کرد
class UserLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

