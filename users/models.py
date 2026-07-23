from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class UserModel(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class UserActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('project_upload', 'Project Upload'),
        ('project_like', 'Project Like'),
        ('project_comment', 'Project Comment'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES,
        default='project_upload'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activities'
    )
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activity Logs'

    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
    )
    notification_type = models.CharField(
        max_length=20,
        choices=[('like', 'Like'), ('chat', 'Chat'), ('system', 'System')],
        default='system',
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To: {self.recipient.email} - {self.notification_type}"
