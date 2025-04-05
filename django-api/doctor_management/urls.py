from django.urls import path, include
from rest_framework.routers import DefaultRouter
from doctor_management import views

router = DefaultRouter()
router.register(r'doctors', views.DoctorProfileViewSet)
router.register(r'specializations', views.SpecializationViewSet)
router.register(r'doctor-availabilities', views.DoctorAvailabilityViewSet)
router.register(r'doctor-time-offs', views.DoctorTimeOffViewSet)

urlpatterns = [
    path('', include(router.urls)),
]