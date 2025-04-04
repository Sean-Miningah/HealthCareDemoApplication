# patients/models.py
from django.db import models
from accounts.models import UserProfile
from core.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class InsuranceProvider(TimeStampedModel):
    """
    Model to store insurance provider details.
    """
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class PatientProfile(UserProfile):
    """
    Extended profile for patients.
    """
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)

    # Medical history fields
    medical_conditions = models.TextField(blank=True, help_text="List of existing medical conditions")
    current_medications = models.TextField(blank=True, help_text="List of current medications")

    def __str__(self):
        return f"Patient: {self.user.email}"


class PatientInsurance(TimeStampedModel):
    """
    Patient insurance information.
    """
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='insurances')
    insurance_provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    policy_holder_name = models.CharField(max_length=100)
    policy_holder_relation = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient.user.email} - {self.insurance_provider.name}"

