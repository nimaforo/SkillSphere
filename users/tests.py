# users/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user_register')  
        self.login_url = reverse('token_obtain_pair')   
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!'
        }

    def test_user_registration_successful(self):
        """تست ثبت‌نام موفق کاربر جدید"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_user_login_and_get_jwt_token(self):
        """تست لاگین و دریافت توکن JWT"""
        User.objects.create_user(**self.user_data)
        
        # فرستادن اطلاعات کامل جهت تطبیق با سریالایزر شما
        login_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)