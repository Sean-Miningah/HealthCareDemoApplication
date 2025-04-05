from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from doctor_management.models import DoctorProfile, Specialization, DoctorAvailability, DoctorTimeOff
from django.urls import reverse
from rest_framework import status


User = get_user_model()

class SpecializationViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            password='adminpassword', email='admin@example.com', role="ADMIN"
        )
        self.user = User.objects.create_user(
            password='testpassword', email="test@example.com"
        )
        self.specialization = Specialization.objects.create(name="Cardiology", description="Heart specialist")

    def test_list_specializations(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('specialization-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_specialization_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('specialization-list')
        data = {'name': 'Neurology', 'description': 'Brain specialist'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_specialization_by_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('specialization-list')
        data = {'name': 'Neurology', 'description': 'Brain specialist'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)