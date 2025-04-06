from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from doctor_management.models import DoctorProfile, Specialization, DoctorAvailability, DoctorTimeOff
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


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

    def test_update_speicialization_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('specialization-detail', args=[self.specialization.id])
        data = {'name': 'Plastic Surgery', 'description': "Plastic surgery specialist"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DoctorProfileViewSet(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            password='adminpassword', email='admin@example.com',
        )
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com', password='doctorpassword', role="DOCTOR", first_name='doctor'
        )
        self.second_doctor_user  = User.objects.create(
            email="seconddoctor@example.com", password="doctor2password", role="DOCTOR", first_name='doctor2'
        )
        self.patient_user = User.objects.create_user(
            email='patient@example.com', password='patientpassword'
        )

        self.specialization = Specialization.objects.create(name='Cardiology', description='Heart specialist')

        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            license_number='12345',
            years_of_experience=5,
            biography='Test bio',
            education='Test education',
            accepting_new_patients=True,
            consultation_fee=100.00,
            address='123 Main St',
            city='Test City',
        )

        self.doctor2_profile =DoctorProfile.objects.create(
            user=self.second_doctor_user,
            license_number='233434',
            years_of_experience=4,
            biography='Test bio',
            education='Test education',
            accepting_new_patients=True,
            consultation_fee=100.00,
            address='123 Main St',
            city='Test City',
        )

        self.doctor_profile.specialization.add(self.specialization)
        self.doctor_availability = DoctorAvailability.objects.create(doctor=self.doctor_profile, day_of_week=0, start_time='01:00', end_time='23:00')
        self.doctor_time_off = DoctorTimeOff.objects.create(
            doctor=self.doctor_profile,
            start_datetime=timezone.now() + timedelta(days=30),
            end_datetime=timezone.now() + timedelta(days=41),
            reason='Vacation'
        )


    def test_list_doctors_by_any_user(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctorprofile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 1)

    def test_list_doctors_with_specialization_filter(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctorprofile-list') + f'?specialization={self.specialization.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user_full_name'], 'Dr. doctor')

    def test_list_doctors_with_accepting_new_patients_filter(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctorprofile-list') + '?accepting_new_patients=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_create_doctor_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctorprofile-list')
        data = {
            'user': {''
                'first_name': 'New',
                'last_name': 'Doctor',
                'email': 'newdoctor@test.com',
                'password': 'password',
                'password_confirmation': 'password',
                'role':'DOCTOR'
            },
            'license_number': '67890',
            'specialization_ids': [self.specialization.id],
            'years_of_experience': 2,
            'biography': 'Another bio',
            'education': 'Another education',
            'accepting_new_patients': True,
            'consultation_fee': 50.00,
            'address': '124 Main St',
            'city': 'Another City',
            'zip_code': '12346',
            'availabilities':[{'day_of_week': 0, 'start_time': '10:00', 'end_time': '17:00'}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DoctorProfile.objects.count() > 0)

    def test_create_doctor_by_non_admin(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctorprofile-list')
        data = {
            'user': {'first_name': 'New', 'last_name': 'Doctor', 'email': 'newdoctor@test.com', 'password': 'password'},
            'license_number': '67890',
            'specialization_ids': [self.specialization.id],
            'years_of_experience': 2,
            'biography': 'Another bio',
            'education': 'Another education',
            'accepting_new_patients': True,
            'consultation_fee': 50.00,
            'address': '124 Main St',
            'city': 'Another City',
            'state': 'TS',
            'zip_code': '12346',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(DoctorProfile.objects.count() > 1)

    def test_get_doctor_me(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctorprofile-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_full_name'], 'Dr. doctor')

    def test_get_doctor_availabilities(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctorprofile-availabilities', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_add_doctor_availability(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctorprofile-add-availability', kwargs={'pk': self.doctor_profile.pk})
        data = {'day_of_week': 1, 'start_time': '10:00', 'end_time': '18:00'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_doctor_availability_unauthorised(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctorprofile-add-availability', kwargs={'pk': self.doctor_profile.pk})
        data = {'day_of_week': 1, 'start_time': '10:00', 'end_time': '18:00'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(DoctorAvailability.objects.count(), 1)

    def test_get_doctor_time_offs(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctorprofile-time-offs', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reason'], 'Vacation')

    def test_add_doctor_time_off(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctorprofile-add-time-off', kwargs={'pk': self.doctor_profile.pk})
        data = {
            'start_datetime': timezone.now() + timedelta(days=2),
            'end_datetime': timezone.now() + timedelta(days=3),
            'reason': 'Sick Leave'
            }
        response = self.client.post(url, data)
        # doctor_time_off = DoctorTimeOff.objects.get(id=response.data.id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorTimeOff.objects.count(), 2)

        time_off_id = response.data['id']
        doctor_time_off = DoctorTimeOff.objects.get(id=time_off_id)
        self.assertEqual(doctor_time_off.reason, data['reason'])

    def test_add_doctor_time_off_unauthorised(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctorprofile-add-time-off', kwargs={'pk': self.doctor_profile.pk})
        data = {'start_datetime': timezone.now() + timedelta(days=2), 'end_datetime': timezone.now() + timedelta(days=3), 'reason': 'Sick Leave'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(DoctorTimeOff.objects.count(), 1)

    def test_available_slots_success(self):
        self.client.force_authenticate(user=self.doctor_user)
        test_date = (timezone.now().date() - timedelta(days=timezone.now().weekday()))
        url = reverse('doctorprofile-available-slots', kwargs={'pk': self.doctor_profile.pk}) + f'?date={test_date.strftime("%Y-%m-%d")}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_available_slots_bad_request(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctorprofile-available-slots', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_doctor_profile_detail(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctorprofile-detail', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_full_name'], 'Dr. doctor')

    def test_update_doctor_profile_by_doctor(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctorprofile-detail', kwargs={'pk': self.doctor_profile.pk})
        data = {'years_of_experience': 10}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DoctorProfile.objects.get(id=self.doctor_profile.id).years_of_experience, 10)

    def test_update_doctor_profile_by_non_doctor_unauthorised(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctorprofile-detail', kwargs={'pk': self.doctor_profile.pk})
        data = {'years_of_experience': 10}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_doctor_profile_by_doctor_unauthorised(self):
        self.client.force_authenticate(user=self.second_doctor_user)
        url = reverse('doctorprofile-detail', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(DoctorProfile.objects.count(), 2)

    def test_delete_doctor_profile_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctorprofile-detail', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DoctorAvailabilityViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            password='adminpassword', email='admin@example.com', role="ADMIN"
        )
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com', password='doctorpassword', role="DOCTOR"
        )
        self.patient_user = User.objects.create_user(
            email='patient@example.com', password='patientpassword', role="PATIENT"
        )