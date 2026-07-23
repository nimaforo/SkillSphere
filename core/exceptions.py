# core/exceptions.py
"""
Custom exception handlers for SkillSphere API
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that adds logging and custom formatting
    """
    
    # Default DRF exception handling
    response = exception_handler(exc, context)
    
    # Log the exception
    logger.error(
        f"Exception occurred: {type(exc).__name__}",
        exc_info=exc,
        extra={
            'request_path': context['request'].path if 'request' in context else None,
            'method': context['request'].method if 'request' in context else None,
            'user': context['request'].user if 'request' in context else None,
        }
    )
    
    # Handle custom exceptions
    if response is not None:
        # Add custom fields to response
        response.data = {
            'status': 'error',
            'code': response.status_code,
            'message': response.data.get('detail', 'An error occurred'),
            'errors': response.data,
        }
    else:
        # Handle exceptions not caught by DRF
        if isinstance(exc, DjangoValidationError):
            data = {
                'status': 'error',
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Validation error',
                'errors': exc.message_dict if hasattr(exc, 'message_dict') else [str(exc)],
            }
            response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, Http404):
            data = {
                'status': 'error',
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Not found',
                'errors': {'detail': 'The requested resource was not found'},
            }
            response = Response(data, status=status.HTTP_404_NOT_FOUND)
        
        elif isinstance(exc, PermissionError):
            data = {
                'status': 'error',
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'Permission denied',
                'errors': {'detail': str(exc)},
            }
            response = Response(data, status=status.HTTP_403_FORBIDDEN)
        
        else:
            # Generic error
            data = {
                'status': 'error',
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An internal error occurred',
                'errors': {'detail': 'Internal server error'},
            }
            response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


class RateLimitExceeded(Exception):
    """
    Raised when rate limit is exceeded
    """
    def __init__(self, message="Rate limit exceeded", wait_time=None):
        self.message = message
        self.wait_time = wait_time
        super().__init__(self.message)


class InvalidTokenException(Exception):
    """
    Raised when JWT token is invalid or expired
    """
    def __init__(self, message="Invalid or expired token"):
        self.message = message
        super().__init__(self.message)


class FileValidationError(Exception):
    """
    Raised when file validation fails
    """
    def __init__(self, message="File validation failed"):
        self.message = message
        super().__init__(self.message)


class UserNotAuthenticatedException(Exception):
    """
    Raised when user is not authenticated
    """
    def __init__(self, message="User not authenticated"):
        self.message = message
        super().__init__(self.message)
