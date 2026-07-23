from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from users.views import register_view, login_view

# Health check endpoint
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'skillsphere-api',
        'version': '1.0.0'
    })

# Test endpoint for debugging
def test_endpoint(request):
    return JsonResponse({
        'message': 'API is working! ✅',
        'method': request.method,
        'user': str(request.user)
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    path('test/', test_endpoint, name='test'),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Auth endpoints
    path('api/register/', register_view, name='register'),
    path('api/login/', login_view, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)