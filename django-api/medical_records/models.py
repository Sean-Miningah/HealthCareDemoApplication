# medical_records/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from patient_management.models import PatientProfile
from doctor_management.models import DoctorProfile
from appointments.models import Appointment

class MedicalRecord(TimeStampedModel):
    """
    Medical record for a patient that can be linked to an appointment.
    """
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.OneToOneField(
        Appointment, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='medical_record'
    )

    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Vitals
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Temperature in °C")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Beats per minute")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Breaths per minute")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")

    # For record tracking
    is_confidential = models.BooleanField(default=False, help_text="Set to true for sensitive records with restricted access")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Medical Record for {self.patient} - {self.created_at.date()}"

    def clean(self):
        # If linked to an appointment, make sure doctor and patient match
        if self.appointment:
            if self.appointment.doctor != self.doctor:
                raise ValidationError(_("The doctor in the record must match the doctor from the appointment"))
            if self.appointment.patient != self.patient:
                raise ValidationError(_("The patient in the record must match the patient from the appointment"))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class MedicalImage(TimeStampedModel):
    """
    Medical images (X-rays, MRIs, etc.) linked to a medical record.
    """
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_file = models.FileField(upload_to='medical_images/%Y/%m/%d/')
    image_type = models.CharField(max_length=50, blank=True, help_text="Type of medical image (X-ray, MRI, etc.)")

    def __str__(self):
        return f"{self.title} - {self.medical_record.patient}"


class MedicalRecordAccess(TimeStampedModel):
    """
    Tracks access to medical records for audit purposes.
    """
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='record_access_logs')
    accessed_at = models.DateTimeField(auto_now_add=True)
    access_reason = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-accessed_at']
        verbose_name_plural = "Medical Record Access Logs"

    def __str__(self):
        return f"{self.user} accessed {self.medical_record} at {self.accessed_at}"