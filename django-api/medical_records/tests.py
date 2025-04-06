from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from medical_records.models import MedicalRecord, MedicalImage, MedicalRecordAccess
from appointments.models import Appointment
from django.utils import timezone
from accounts.models import User
from doctor_management.models import DoctorProfile
from patient_management.models import PatientProfile
from django.core.files.uploadedfile import SimpleUploadedFile


class MedicalRecordViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            password='adminpassword', email='admin@example.com', role="ADMIN"
        )
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com', password='doctorpassword', role="DOCTOR", first_name='doctor',
        )
        self.second_doctor_user = User.objects.create(
            email="seconddoctor@example.com", password="doctor2password", role="DOCTOR", first_name='doctor2'
        )
        self.patient_user = User.objects.create_user(
            email='patient@example.com', password='patientpassword', role="PATIENT"
        )
        self.second_patient_user = User.objects.create_user(
            email='patient2@example.com', password='patient2password', role="PATIENT"
        )

        self.doctor_profile = DoctorProfile.objects.create(user=self.doctor_user, license_number="2345")
        self.second_doctor_profile = DoctorProfile.objects.create(user=self.second_doctor_user, license_number="432")
        self.patient_profile = PatientProfile.objects.create(user=self.patient_user)
        self.second_patient_profile = PatientProfile.objects.create(user=self.second_patient_user)

        dummy_file = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded_file1 = SimpleUploadedFile('dummy_file1.gif', dummy_file, content_type='image/gif')
        self.uploaded_file2 = SimpleUploadedFile('dummy_file2.gif', dummy_file, content_type='image/gif')

        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient_profile, doctor=self.doctor_profile)
        self.second_medical_record = MedicalRecord.objects.create(
            patient=self.second_patient_profile, doctor=self.second_doctor_profile)
        self.medical_image = MedicalImage.objects.create(
            medical_record=self.medical_record, title="X-Ray", image_file=self.uploaded_file2)
        self.medical_record_access = MedicalRecordAccess.objects.create(
            medical_record=self.medical_record, user=self.doctor_user, access_reason="Test")

        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        self.doctor_client = APIClient()
        self.doctor_client.force_authenticate(user=self.doctor_user)

        self.second_doctor_client = APIClient()
        self.second_doctor_client.force_authenticate(user=self.second_doctor_user)

        self.patient_client = APIClient()
        self.patient_client.force_authenticate(user=self.patient_user)

        self.second_patient_client = APIClient()
        self.second_patient_client.force_authenticate(user=self.second_patient_user)

        self.client = APIClient()
        self.client.force_authenticate(user=self.doctor_user)

    def test_medical_record_list_admin(self):
        url = reverse('medicalrecord-list')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_medical_record_list_doctor(self):
        url = reverse('medicalrecord-list')
        response = self.doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.second_doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_record_list_patient(self):
        url = reverse('medicalrecord-list')
        response = self.patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.second_patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_record_create_doctor(self):
        url = reverse('medicalrecord-list')
        data = {'patient': self.patient_profile.id, 'diagnosis': 'Test Diagnosis', 'doctor': self.doctor_profile.id}
        response = self.doctor_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalRecord.objects.count(), 3)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_record_create_patient(self):
        url = reverse('medicalrecord-list')
        data = {'patient': self.patient_profile.id, 'diagnosis': 'Test Diagnosis'}
        response = self.patient_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_medical_record_update_doctor(self):
        url = reverse('medicalrecord-detail', args=[self.medical_record.id])
        data = {'diagnosis': 'Updated Diagnosis'}
        response = self.doctor_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MedicalRecord.objects.get(id=self.medical_record.id).diagnosis, 'Updated Diagnosis')
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_record_update_other_doctor(self):
        url = reverse('medicalrecord-detail', args=[self.second_medical_record.id])
        data = {'diagnosis': 'Updated Diagnosis'}
        response = self.doctor_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_medical_record_retrieve(self):
        url = reverse('medicalrecord-detail', args=[self.medical_record.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_record_my_records(self):
        url = reverse('medicalrecord-my-records')
        response = self.patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_record_access_logs(self):
        MedicalRecordAccess.objects.create(medical_record=self.medical_record, user=self.doctor_user, access_reason="Test")
        url = reverse('medicalrecord-access-logs', args=[self.medical_record.id])
        response = self.doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_medical_record_add_image(self):
        # Create a new file for this test instead of reusing self.uploaded_file2
        dummy_file = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        fresh_file = SimpleUploadedFile('new_test_image.gif', dummy_file, content_type='image/gif')

        url = reverse('medicalrecord-add-image', args=[self.medical_record.id])
        data = {'title': 'Test Image', 'image_file': fresh_file}
        response = self.doctor_client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalImage.objects.count(), 2)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_image_list_admin(self):
        url = reverse('medicalimage-list')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_image_list_doctor(self):
        url = reverse('medicalimage-list')
        response = self.doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        MedicalImage.objects.create(medical_record=self.second_medical_record, title="X-Ray", image_file="test.jpg")
        response = self.second_doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_image_list_patient(self):
        url = reverse('medicalimage-list')
        response = self.patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        MedicalImage.objects.create(medical_record=self.second_medical_record, title="X-Ray", image_file=self.uploaded_file1)
        response = self.second_patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_image_create_doctor(self):
        url = reverse('medicalimage-list')

        data = {'medical_record': self.medical_record.id, 'title': 'Test Image', 'image_file': self.uploaded_file1}
        response = self.doctor_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalImage.objects.count(), 2)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_image_create_patient(self):
        url = reverse('medicalimage-list')
        data = {'medical_record': self.medical_record.id, 'title': 'Test Image', 'image_file': self.uploaded_file1}
        response = self.patient_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_medical_image_update_doctor(self):
        url = reverse('medicalimage-detail', args=[self.medical_image.id])
        data = {'title': 'Updated Image'}
        response = self.doctor_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MedicalImage.objects.get(id=self.medical_image.id).title, 'Updated Image')
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_image_update_other_doctor(self):
        other_image = MedicalImage.objects.create(medical_record=self.second_medical_record, title="X-Ray", image_file="test.jpg")
        url = reverse('medicalimage-detail', args=[other_image.id])
        data = {'title': 'Updated Image'}
        response = self.doctor_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_medical_image_delete_doctor(self):
        url = reverse('medicalimage-detail', args=[self.medical_image.id])
        response = self.doctor_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MedicalImage.objects.count(), 0)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_image_delete_other_doctor(self):
        other_image = MedicalImage.objects.create(medical_record=self.second_medical_record, title="X-Ray", image_file="test.jpg")
        url = reverse('medicalimage-detail', args=[other_image.id])
        response = self.doctor_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_medical_image_retrieve(self):
        url = reverse('medicalimage-detail', args=[self.medical_image.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MedicalRecordAccess.objects.count(), 2)

    def test_medical_record_access_list_admin(self):
        url = reverse('medicalrecordaccess-list')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_record_access_list_doctor(self):
        url = reverse('medicalrecordaccess-list')
        response = self.doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        MedicalRecordAccess.objects.create(medical_record=self.second_medical_record, user=self.second_doctor_user, access_reason="Test")
        response = self.second_doctor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_medical_record_access_list_patient(self):
        url = reverse('medicalrecordaccess-list')
        response = self.patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        MedicalRecordAccess.objects.create(medical_record=self.second_medical_record, user=self.second_patient_user, access_reason="Test")
        response = self.second_patient_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
