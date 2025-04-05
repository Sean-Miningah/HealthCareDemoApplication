from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patient_management import views

router = DefaultRouter()
router.register(r'patients', views.PatientProfileViewSet)
router.register(r'insurance-providers', views.InsuranceProviderViewSet)
router.register(r'patient-insurances', views.PatientInsuranceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]