# users/adapters/serializers.py
from rest_framework import serializers
from users.domain.entities import UserEntity
from users.adapters.db_repository import DjangoUserRepositoryAdapter
from datetime import datetime

class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        repository = DjangoUserRepositoryAdapter()
        if repository.get_by_username(value):
            raise serializers.ValidationError("این نام کاربری قبلاً استفاده شده است.")
        return value

    def validate_email(self, value):
        repository = DjangoUserRepositoryAdapter()
        if repository.get_by_email(value):
            raise serializers.ValidationError("کاربری با این ایمیل قبلاً ثبت‌نام کرده است.")
        return value

    def create(self, validated_data):
        repository = DjangoUserRepositoryAdapter()
        
        user_entity = UserEntity(
            id=None,
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=True,
            created_at=datetime.now()
        )
        
        new_user = repository.create(user_entity, validated_data['password'])
        
        # فراخوانی تسک سلری به صورت آسنکرون (پس‌زمینه) با متد .delay()
        from users.tasks import send_welcome_email_task
        send_welcome_email_task.delay(new_user.email, new_user.username)
        
        return new_user