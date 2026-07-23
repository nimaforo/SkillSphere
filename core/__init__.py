# core/__init__.py
# Celery integration (optional)
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    print("⚠️ Celery not installed. Background tasks will be disabled.")
    pass
