# core/validators.py
"""
Custom validators for SkillSphere
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_email(email):
    """
    Validate email address
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValidationError(_('Invalid email address'))


def validate_username(username):
    """
    Validate username
    - 3-30 characters
    - Alphanumeric, underscores, hyphens
    """
    if len(username) < 3 or len(username) > 30:
        raise ValidationError(_('Username must be between 3 and 30 characters'))
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationError(_('Username can only contain letters, numbers, underscores, and hyphens'))


def validate_password_strength(password):
    """
    Validate password strength
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        raise ValidationError(_('Password must be at least 8 characters long'))
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(_('Password must contain at least one uppercase letter'))
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(_('Password must contain at least one lowercase letter'))
    
    if not re.search(r'[0-9]', password):
        raise ValidationError(_('Password must contain at least one digit'))
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(_('Password must contain at least one special character'))


def validate_file_size(file_obj, max_size_mb=10):
    """
    Validate file size
    
    Args:
        file_obj: File object
        max_size_mb: Maximum size in MB
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        raise ValidationError(
            _('File size cannot exceed %(max_size)s MB') % {'max_size': max_size_mb}
        )


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension
    
    Args:
        filename: File name
        allowed_extensions: List of allowed extensions (e.g., ['pdf', 'jpg', 'png'])
    """
    ext = filename.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _('File type not allowed. Allowed types: %(extensions)s') % 
            {'extensions': ', '.join(allowed_extensions)}
        )


def validate_text_input(text, min_length=1, max_length=5000, allow_html=False):
    """
    Validate text input
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        allow_html: Allow HTML tags
    """
    if len(text) < min_length:
        raise ValidationError(
            _('Text must be at least %(min)d characters') % {'min': min_length}
        )
    
    if len(text) > max_length:
        raise ValidationError(
            _('Text cannot exceed %(max)d characters') % {'max': max_length}
        )
    
    # Check for potentially harmful content
    if not allow_html:
        if re.search(r'<[^>]+>', text):
            raise ValidationError(_('HTML tags are not allowed'))
    
    # Check for script tags (even if HTML is allowed)
    if re.search(r'<script|javascript:', text, re.IGNORECASE):
        raise ValidationError(_('Scripts are not allowed'))


def validate_phone_number(phone):
    """
    Validate phone number (international format)
    """
    phone_regex = r'^\+?[1-9]\d{1,14}$'
    if not re.match(phone_regex, phone):
        raise ValidationError(_('Invalid phone number'))


def validate_url(url):
    """
    Validate URL
    """
    url_regex = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    if not re.match(url_regex, url):
        raise ValidationError(_('Invalid URL'))
