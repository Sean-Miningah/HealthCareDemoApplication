from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from appointments.models import Appointment, AppointmentType, AppointmentReminder
from patient_management.models import PatientProfile
from doctor_management.models import DoctorProfile, DoctorAvailability, DoctorTimeOff
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class AppointmentTypeViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com', password='adminpassword', role="ADMIN"
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        self.appointment_type = AppointmentType.objects.create(
            name='Checkup', description='Routine checkup', duration_minutes=30
        )

    def test_list_appointment_types(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointmenttype-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_appointment_type_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointmenttype-list')
        data = {'name': 'Consultation', 'description': 'Medical consultation', 'duration_minutes': 60}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppointmentType.objects.count(), 2)

    def test_create_appointment_type_unauthenticated(self):
        url = reverse('appointmenttype-list')
        data = {'name': 'Consultation', 'description': 'Medical consultation', 'duration_minutes': 60}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_appointment_type_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointmenttype-detail', args=[self.appointment_type.id])
        data = {'name': 'Updated Checkup'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AppointmentType.objects.get(id=self.appointment_type.id).name, 'Updated Checkup')

    def test_delete_appointment_type_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointmenttype-detail', args=[self.appointment_type.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AppointmentType.objects.count(), 0)


class AppointmentViewSetTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com', password='adminpassword', role="ADMIN"
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Create patient user
        self.patient_user = User.objects.create_user(
            email='patient@example.com', password='patientpassword', role="PATIENT"
        )
        self.patient_token = Token.objects.create(user=self.patient_user)
        self.patient_profile = PatientProfile.objects.create(user=self.patient_user)

        # Create doctor user
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com', password='doctorpassword', role="DOCTOR"
        )
        self.doctor_token = Token.objects.create(user=self.doctor_user)
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            license_number="12345"  # Required field
        )

        # Create appointment type
        self.appointment_type = AppointmentType.objects.create(
            name='Checkup', description='Routine checkup', duration_minutes=30
        )

        # Create doctor availability for all weekdays to ensure tests work
        # regardless of which day the test runs
        for day in range(7):  # 0-6 for Monday-Sunday
            DoctorAvailability.objects.create(
                doctor=self.doctor_profile,
                day_of_week=day,
                start_time=timezone.now().time(),
                end_time=(timezone.now() + timedelta(hours=8)).time()
            )

        # Now create the appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor_profile,
            appointment_type=self.appointment_type,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, minutes=30)
        )

    def test_list_appointments_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_appointments_doctor(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
        url = reverse('appointment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_appointments_patient(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
        url = reverse('appointment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_appointment_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointment-detail', args=[self.appointment.id])
        data = {'status': 'CONFIRMED'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.get(id=self.appointment.id).status, 'CONFIRMED')

    def test_update_appointment_doctor(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
        url = reverse('appointment-detail', args=[self.appointment.id])
        data = {'status': 'COMPLETED'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.get(id=self.appointment.id).status, 'COMPLETED')

    def test_update_appointment_patient_cancel(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
        url = reverse('appointment-detail', args=[self.appointment.id])
        data = {'status': 'CANCELLED'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.get(id=self.appointment.id).status, 'CANCELLED')

    def test_create_appointment_patient(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
        url = reverse('appointment-list')

        new_start = timezone.now() + timedelta(days=2)
        new_end = new_start + timedelta(minutes=30)

        data = {
            'patient': self.patient_profile.id,
            'doctor': self.doctor_profile.id,
            'appointment_type': self.appointment_type.id,
            'start_datetime': new_start.isoformat(),
            'end_datetime': new_end.isoformat(),
            'create_reminder': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_create_appointment_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointment-list')

        new_start = timezone.now() + timedelta(days=3)
        new_end = new_start + timedelta(minutes=30)

        data = {
            'patient': self.patient_profile.id,
            'doctor': self.doctor_profile.id,
            'appointment_type': self.appointment_type.id,
            'start_datetime': new_start.isoformat(),
            'end_datetime': new_end.isoformat(),
            'create_reminder': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_delete_appointment_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('appointment-detail', args=[self.appointment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_reschedule_appointment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
        url = reverse('appointment-reschedule', args=[self.appointment.id])
        new_start_datetime = timezone.now() + timedelta(days=2)
        data = {'new_start_datetime': new_start_datetime.isoformat()}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
        self.assertEqual(Appointment.objects.get(id=self.appointment.id).status, 'RESCHEDULED')

    def test_my_appointments_patient(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
        url = reverse('appointment-my-appointments')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_doctor_schedule(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
        url = reverse('appointment-doctor-schedule')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_appointment_with_reminder(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
        url = reverse('appointment-list')

        new_start = timezone.now() + timedelta(days=4)
        new_end = new_start + timedelta(minutes=30)

        data = {
            'patient': self.patient_profile.id,
            'doctor': self.doctor_profile.id,
            'appointment_type': self.appointment_type.id,
            'start_datetime': new_start.isoformat(),
            'end_datetime': new_end.isoformat(),
            'create_reminder': True,
            'reminder_hours_before': 24,
            'reminder_type': 'EMAIL'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
        self.assertEqual(AppointmentReminder.objects.count(), 1)


# class AppointmentReminderViewSetTests(APITestCase):
#     def setUp(self):
#         self.admin_user = User.objects.create_superuser(
#             email='admin@example.com', password='adminpassword'
#         )
#         self.admin_token = Token.objects.create(user=self.admin_user)

#         self.patient_user = User.objects.create_user(
#             email='patient@example.com', password='patientpassword'
#         )
#         self.patient_profile = PatientProfile.objects.create(user=self.patient_user)
#         self.patient_token = Token.objects.create(user=self.patient_user)

#         self.doctor_user = User.objects.create_user(
#             email='doctor@example.com', password='doctorpassword'
#         )
#         self.doctor_profile = DoctorProfile.objects.create(user=self.doctor_user)
#         self.doctor_token = Token.objects.create(user=self.doctor_user)

#         self.appointment_type = AppointmentType.objects.create(
#             name='Checkup', description='Routine checkup', duration_minutes=30
#         )

#         self.appointment = Appointment.objects.create(
#             patient=self.patient_profile,
#             doctor=self.doctor_profile,
#             appointment_type=self.appointment_type,
#             start_datetime=timezone.now() + timedelta(days=1),
#             end_datetime=timezone.now() + timedelta(days=1, minutes=30)
#         )

#         self.reminder = AppointmentReminder.objects.create(
#             appointment=self.appointment,
#             reminder_type='EMAIL',
#             scheduled_time=timezone.now() + timedelta(hours=23),
#             message='Test reminder'
#         )

#     def test_list_reminders_admin(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
#         url = reverse('appointmentreminder-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_list_reminders_doctor(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
#         url = reverse('appointmentreminder-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_list_reminders_patient(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
#         url = reverse('appointmentreminder-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_create_reminder_admin(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
#         url = reverse('appointmentreminder-list')
#         data = {
#             'appointment': self.appointment.id,
#             'reminder_type': 'SMS',
#             'scheduled_time': (timezone.now() + timedelta(hours=22)).isoformat(),
#             'message': 'New test reminder'
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(AppointmentReminder.objects.count(), 2)

#     def test_create_reminder_doctor(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
#         url = reverse('appointmentreminder-list')
#         data = {
#             'appointment': self.appointment.id,
#             'reminder_type': 'SMS',
#             'scheduled_time': (timezone.now() + timedelta(hours=22)).isoformat(),
#             'message': 'New test reminder'
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(AppointmentReminder.objects.count(), 2)

#     def test_create_reminder_patient(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
#         url = reverse('appointmentreminder-list')
#         data = {
#             'appointment': self.appointment.id,
#             'reminder_type': 'SMS',
#             'scheduled_time': (timezone.now() + timedelta(hours=22)).isoformat(),
#             'message': 'New test reminder'
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(AppointmentReminder.objects.count(), 2)

#     def test_update_reminder_admin(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
#         url = reverse('appointmentreminder-detail', args=[self.reminder.id])
#         data = {'message': 'Updated test reminder'}
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(AppointmentReminder.objects.get(id=self.reminder.id).message, 'Updated test reminder')

#     def test_update_reminder_doctor(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
#         url = reverse('appointmentreminder-detail', args=[self.reminder.id])
#         data = {'message': 'Updated test reminder'}
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(AppointmentReminder.objects.get(id=self.reminder.id).message, 'Updated test reminder')

#     def test_update_reminder_patient(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
#         url = reverse('appointmentreminder-detail', args=[self.reminder.id])
#         data = {'message': 'Updated test reminder'}
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(AppointmentReminder.objects.get(id=self.reminder.id).message, 'Updated test reminder')

#     def test_delete_reminder_admin(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
#         url = reverse('appointmentreminder-detail', args=[self.reminder.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(AppointmentReminder.objects.count(), 0)

#     def test_delete_reminder_doctor(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.doctor_token.key)
#         url = reverse('appointmentreminder-detail', args=[self.reminder.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(AppointmentReminder.objects.count(), 0)

#     def test_delete_reminder_patient(self):
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.patient_token.key)
#         url = reverse('appointmentreminder-detail', args=[self.reminder.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(AppointmentReminder.objects.count(), 0)
