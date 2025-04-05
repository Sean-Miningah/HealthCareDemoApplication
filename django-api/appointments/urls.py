from django.urls import path, include
from rest_framework.routers import DefaultRouter
from appointments import views

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'appointment-types', views.AppointmentTypeViewSet)
router.register(r'appointment-reminders', views.AppointmentReminderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]