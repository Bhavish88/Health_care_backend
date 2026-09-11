"""
URL configuration for healthcare_project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    """
    Healthcare Backend API Root
    Provides an overview and quick links to all available endpoints.
    """
    return Response({
        'title': 'Healthcare Management System API',
        'status': 'online',
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/ [POST]',
                'login': '/api/auth/login/ [POST]',
            },
            'patients': {
                'list_create': '/api/patients/ [GET, POST]',
                'detail_update_delete': '/api/patients/<id>/ [GET, PUT, DELETE]',
            },
            'doctors': {
                'list_create': '/api/doctors/ [GET, POST]',
                'detail_update_delete': '/api/doctors/<id>/ [GET, PUT, DELETE]',
            },
            'mappings': {
                'list_create': '/api/mappings/ [GET, POST]',
                'patient_doctors': '/api/mappings/<patient_id>/ [GET]',
                'delete_mapping': '/api/mappings/<id>/ [DELETE]',
            },
        }
    })


urlpatterns = [
    path('', api_root_view, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/mappings/', include('mappings.urls')),
]
