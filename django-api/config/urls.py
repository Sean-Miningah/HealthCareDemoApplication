from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API schema documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="Healthcare Appointment API",
        default_version='v1',
        description="API for healthcare appointment scheduling system",
        terms_of_service="https://www.gogole.com/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include([
        path('accounts/', include('accounts.urls')),
        path('patients/', include('patient_management.urls')),
        path('doctors/', include('doctor_management.urls')),
        path('appointments/', include('appointments.urls')),
        path('medical-records/', include('medical_records.urls')),
        # API documentation
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
