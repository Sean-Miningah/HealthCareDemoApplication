# appointments/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
from doctor_management.models import DoctorProfile, DoctorTimeOff
from patient_management.models import PatientProfile
from django.utils.translation import gettext_lazy as _

class AppointmentType(TimeStampedModel):
    """
    Different types of appointments with duration and cost.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    color_hex = models.CharField(max_length=7, default="#3498db", help_text="Color for calendar visualization")

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"


class Appointment(TimeStampedModel):
    """
    Appointment between a doctor and a patient.
    """
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
        ('RESCHEDULED', 'Rescheduled'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_virtual = models.BooleanField(default=False)

    # For virtual appointments
    meeting_link = models.URLField(blank=True, null=True)

    # Fields for managing appointment history
    original_appointment = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rescheduled_appointments'
    )

    class Meta:
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['doctor', 'start_datetime']),
            models.Index(fields=['patient', 'start_datetime']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.patient} appointment with {self.doctor} on {self.start_datetime}"

    def clean(self):
        """
        Validate that:
        1. start_datetime is before end_datetime
        2. No overlapping appointments for the doctor or patient
        3. Check if doctor is available at this time
        """
        if not self.start_datetime or not self.end_datetime:
            return  # These will be checked by field validators

        # Check Start time before end time
        if self.start_datetime >= self.end_datetime:
            raise ValidationError(_("Start time must be before end time"))

        # Check No overlapping appointments for the doctor
        if self.id:  # If this is an existing record
            overlaps_doctor = Appointment.objects.filter(
                doctor=self.doctor,
                status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS']
            ).exclude(id=self.id)
        else:  # If this is a new record
            overlaps_doctor = Appointment.objects.filter(
                doctor=self.doctor,
                status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS']
            )

        for overlap in overlaps_doctor:
            if (self.start_datetime < overlap.end_datetime and
                self.end_datetime > overlap.start_datetime):
                raise ValidationError(_(
                    f"The doctor already has an appointment from {overlap.start_datetime} to {overlap.end_datetime}"
                ))

        # Check No overlapping appointments for the patient
        if self.id:  # If this is an existing record
            overlaps_patient = Appointment.objects.filter(
                patient=self.patient,
                status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS']
            ).exclude(id=self.id)
        else:  # If this is a new record
            overlaps_patient = Appointment.objects.filter(
                patient=self.patient,
                status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS']
            )

        for overlap in overlaps_patient:
            if (self.start_datetime < overlap.end_datetime and
                self.end_datetime > overlap.start_datetime):
                raise ValidationError(_(
                    f"The patient already has an appointment from {overlap.start_datetime} to {overlap.end_datetime}"
                ))

        # Check Doctor not on time off
        time_offs = DoctorTimeOff.objects.filter(doctor=self.doctor)
        for time_off in time_offs:
            if (self.start_datetime < time_off.end_datetime and
                self.end_datetime > time_off.start_datetime):
                raise ValidationError(_(
                    f"The doctor is not available from {time_off.start_datetime} to {time_off.end_datetime}"
                ))

        # Check Appointment within doctor's regular hours
        appointment_day = self.start_datetime.weekday()
        appointment_start_time = self.start_datetime.time()
        appointment_end_time = self.end_datetime.time()

        availabilities = self.doctor.availabilities.filter(day_of_week=appointment_day)

        if not availabilities.exists():
            raise ValidationError(_("The doctor does not work on this day"))

        is_within_hours = False
        for availability in availabilities:
            if (appointment_start_time >= availability.start_time and
                appointment_end_time <= availability.end_time):
                is_within_hours = True
                break

        if not is_within_hours:
            raise ValidationError(_("The appointment time is outside the doctor's working hours"))

    def save(self, *args, **kwargs):
        # If appointment_type is provided but end_datetime isn't calculated
        if self.appointment_type and not self.end_datetime and self.start_datetime:
            duration = self.appointment_type.duration_minutes
            self.end_datetime = self.start_datetime + timezone.timedelta(minutes=duration)

        self.clean()
        super().save(*args, **kwargs)


class AppointmentReminder(TimeStampedModel):
    """
    Reminders for upcoming appointments.
    """
    REMINDER_TYPE_CHOICES = (
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('BOTH', 'Both'),
    )

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES, default='EMAIL')
    scheduled_time = models.DateTimeField()
    message = models.TextField(blank=True)
    sent = models.BooleanField(default=False)
    sent_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reminder for {self.appointment} at {self.scheduled_time}"

    def clean(self):
        if self.scheduled_time >= self.appointment.start_datetime:
            raise ValidationError(_("Reminder must be scheduled before the appointment time"))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)