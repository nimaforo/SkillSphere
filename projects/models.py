# C:/Users/nimaf/web project/webproject/projects/models.py
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# تابع ولیدیتور برای حجم فایل (حداکثر ۱۰ مگابایت)
def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("حجم فایل نمی‌تواند بیشتر از ۱۰ مگابایت باشد.")
    return value

# تابع موقت برای ساکت کردن ارور مایکریشن قدیمی
def validate_file_extension_and_size(value):
    return validate_file_size(value)

class Project(models.Model):  
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='projects'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='project_files/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'zip', 'jpg', 'jpeg', 'png']),
            validate_file_size
        ]
    )
    
    # تھمبنیل image (Celery task سے بنایا جاتا ہے)
    file_thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True,
        help_text="خودکار طور پر منتخب فائلوں کے لیے بنایا جاتا ہے"
    )
    
    # رابطه چندبه‌چند برای ذخیره لایک‌های کاربران روی پروژه
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # متد شمارش تعداد کل لایک‌ها
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


# 🌟 مدل کامنت جدید برای حل ارور ImportError و ساخت سیستم کامنت‌ها
class ProjectComment(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='project_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.email} on {self.project.title}"