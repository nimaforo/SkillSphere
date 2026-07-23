# core/security.py
"""
Security utilities for SkillSphere
"""

import hashlib
import secrets
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter using cache
    """
    
    @staticmethod
    def check_rate_limit(key, limit=10, window=60):
        """
        Check if rate limit is exceeded
        
        Args:
            key: Rate limit key (e.g., 'user_123_login')
            limit: Number of requests allowed
            window: Time window in seconds
        
        Returns:
            Tuple (allowed: bool, remaining: int, reset_time: int)
        """
        from django.core.cache import cache
        
        current = cache.get(key, 0)
        remaining = limit - current
        
        if current >= limit:
            reset_time = cache.ttl(key) or window
            logger.warning(f'Rate limit exceeded for {key}')
            return False, remaining, reset_time
        
        cache.incr(key)
        if cache.ttl(key) == -1:  # First time
            cache.expire(key, window)
        
        return True, remaining, 0
    
    @staticmethod
    def reset_rate_limit(key):
        """
        Reset rate limit for a key
        """
        from django.core.cache import cache
        cache.delete(key)


class TokenManager:
    """
    Token generation and validation
    """
    
    @staticmethod
    def generate_token(length=32):
        """
        Generate a secure random token
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_token(token):
        """
        Hash a token using SHA256
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_verification_token():
        """
        Generate email verification token
        """
        return TokenManager.generate_token(32)
    
    @staticmethod
    def generate_password_reset_token():
        """
        Generate password reset token
        """
        return TokenManager.generate_token(32)


class PasswordManager:
    """
    Password-related security utilities
    """
    
    @staticmethod
    def is_password_compromised(password):
        """
        Check if password is in common password list
        This is a simple implementation - consider using external APIs in production
        """
        common_passwords = [
            'password', '123456', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', 'dragon'
        ]
        return password.lower() in common_passwords
    
    @staticmethod
    def suggest_password():
        """
        Generate a strong password suggestion
        """
        import string
        
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(chars) for _ in range(16))
        return password


class AuditLogger:
    """
    Audit logging for security events
    """
    
    SECURITY_LOGGER = logging.getLogger('django.security')
    
    @staticmethod
    def log_login(user, ip_address=None):
        """Log successful login"""
        AuditLogger.SECURITY_LOGGER.info(
            f'User {user.email} logged in from {ip_address}',
            extra={'user_id': user.id, 'ip': ip_address}
        )
    
    @staticmethod
    def log_failed_login(email, ip_address=None):
        """Log failed login attempt"""
        AuditLogger.SECURITY_LOGGER.warning(
            f'Failed login attempt for {email} from {ip_address}',
            extra={'email': email, 'ip': ip_address}
        )
    
    @staticmethod
    def log_password_change(user, ip_address=None):
        """Log password change"""
        AuditLogger.SECURITY_LOGGER.info(
            f'User {user.email} changed password',
            extra={'user_id': user.id, 'ip': ip_address}
        )
    
    @staticmethod
    def log_email_change(user, old_email, new_email, ip_address=None):
        """Log email change"""
        AuditLogger.SECURITY_LOGGER.warning(
            f'User {old_email} changed email to {new_email}',
            extra={'user_id': user.id, 'old_email': old_email, 'new_email': new_email, 'ip': ip_address}
        )
    
    @staticmethod
    def log_suspicious_activity(user, activity, ip_address=None):
        """Log suspicious activity"""
        AuditLogger.SECURITY_LOGGER.error(
            f'Suspicious activity detected for {user.email if user else "unknown"}: {activity}',
            extra={'user_id': user.id if user else None, 'activity': activity, 'ip': ip_address}
        )


class IPWhitelist:
    """
    IP whitelist management
    """
    
    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_ip_allowed(ip_address, whitelist=None):
        """
        Check if IP is in whitelist
        """
        if not whitelist:
            return True  # No whitelist configured
        
        return ip_address in whitelist
    
    @staticmethod
    def is_ip_blocked(ip_address):
        """
        Check if IP is blocked
        """
        from django.core.cache import cache
        
        blocked_key = f'blocked_ip_{ip_address}'
        return cache.get(blocked_key, False)
    
    @staticmethod
    def block_ip(ip_address, duration_minutes=60):
        """
        Block IP for specified duration
        """
        from django.core.cache import cache
        
        blocked_key = f'blocked_ip_{ip_address}'
        cache.set(blocked_key, True, duration_minutes * 60)
        logger.warning(f'IP {ip_address} blocked for {duration_minutes} minutes')


class CSRFProtection:
    """
    CSRF protection utilities
    """
    
    @staticmethod
    def validate_csrf_token(request):
        """
        Validate CSRF token
        """
        from django.middleware.csrf import CsrfViewMiddleware
        
        middleware = CsrfViewMiddleware(lambda r: None)
        try:
            middleware.process_request(request)
            return True
        except Exception:
            return False


class SQLinjectionPrevention:
    """
    SQL Injection prevention utilities
    """
    
    @staticmethod
    def sanitize_search_query(query):
        """
        Sanitize search query to prevent SQL injection
        Always use Django ORM and parameterized queries instead of raw SQL!
        """
        # Remove special SQL characters
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            query = query.replace(char, '')
        
        return query.strip()


class XSSPrevention:
    """
    XSS prevention utilities
    """
    
    @staticmethod
    def sanitize_html(html_content):
        """
        Sanitize HTML content
        """
        import bleach
        
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
        allowed_attributes = {'a': ['href', 'title']}
        
        return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)
    
    @staticmethod
    def escape_html(text):
        """
        Escape HTML special characters
        """
        from django.utils.html import escape
        return escape(text)
