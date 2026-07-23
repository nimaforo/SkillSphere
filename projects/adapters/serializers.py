# projects/adapters/serializers.py
from rest_framework import serializers
from projects.domain.entities import ProjectEntity
import os

class ProjectCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), 
        required=False, 
        default=[]
    )

    def validate_file(self, value):
        # بررسی حجم فایل (حداکثر ۵۰ مگابایت)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError("حجم فایل نباید بیشتر از ۵۰ مگابایت باشد.")
        
        # بررسی پسوندهای مجاز
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.pdf', '.zip', '.rar', '.jpg', '.jpeg', '.png']
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"پسوند {ext} مجاز نیست. پسوندهای مجاز: {', '.join(valid_extensions)}")
        
        return value

    def save(self):
        from datetime import datetime
        request = self.context.get('request')
        user = request.user
        
        validated_data = self.validated_data
        uploaded_file = validated_data['file']
        
        # ساخت یک آبجکت موقت از انتیتی برای پاس دادن به ریلیشن‌ها
        project_entity = ProjectEntity(
            id=None,
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            file_url='',  # آداپتور دیتابیس آدرس نهایی آپلود را هندل می‌کند
            file_size=uploaded_file.size,
            user_id=user.id,
            created_at=datetime.now(),
            tags=validated_data.get('tags', [])
        )
        
        # ارسال اطلاعات به ریپازیتوری دیتابیس برای ذخیره نهایی
        from projects.adapters.db_repository import DjangoProjectRepositoryAdapter
        repository = DjangoProjectRepositoryAdapter()
        return repository.create(project_entity, uploaded_file)