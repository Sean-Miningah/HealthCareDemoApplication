from django.urls import path, include
from rest_framework.routers import DefaultRouter
from medical_records import views

router = DefaultRouter()
router.register(r'medical-records', views.MedicalRecordViewSet)
router.register(r'medical-images', views.MedicalImageViewSet)
router.register(r'access-logs', views.MedicalRecordAccessViewSet)

urlpatterns = [
    path('', include(router.urls)),
]