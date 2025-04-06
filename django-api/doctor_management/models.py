# doctors/models.py
from django.db import models
from accounts.models import UserProfile
from core.models import TimeStampedModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Specialization(TimeStampedModel):
    """
    Medical specialization (e.g., Cardiology, Neurology, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class DoctorProfile(UserProfile):
    """
    Extended profile for doctors.
    """
    specialization = models.ManyToManyField(Specialization, related_name='doctors_specializations')
    license_number = models.CharField(max_length=100, unique=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    biography = models.TextField(blank=True)
    education = models.TextField(blank=True)
    accepting_new_patients = models.BooleanField(default=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class DoctorAvailability(TimeStampedModel):
    """
    Schedule of when a doctor is available for appointments.
    """
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = "Doctor Availability"
        verbose_name_plural = "Doctor Availabilities"
        unique_together = ('doctor', 'day_of_week', 'start_time')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"

    def clean(self):
        """
        Validate that:
        1. start_time is before end_time
        2. No overlapping time slots for the same doctor on the same day
        """
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(_("Start time must be before end time"))

        # Check for overlapping availabilities
        if self.id:  # If this is an existing record
            overlaps = DoctorAvailability.objects.filter(
                doctor=self.doctor,
                day_of_week=self.day_of_week
            ).exclude(id=self.id)
        else:  # If this is a new record
            overlaps = DoctorAvailability.objects.filter(
                doctor=self.doctor,
                day_of_week=self.day_of_week
            )

        for overlap in overlaps:
            if (self.start_time <= overlap.end_time and
                self.end_time >= overlap.start_time):
                raise ValidationError(_(
                    f"This availability overlaps with {overlap.start_time} - {overlap.end_time}"
                ))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class DoctorTimeOff(TimeStampedModel):
    """
    Records when a doctor is not available (vacation, sick leave, etc.)
    """
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='time_offs')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Doctor Time Off"
        verbose_name_plural = "Doctor Time Offs"
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.doctor} - Time Off ({self.start_datetime} to {self.end_datetime})"

    def clean(self):
        """
        Validate that:
        1. start_datetime is before end_datetime
        2. No overlapping time-offs for the same doctor
        """
        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValidationError(_("Start datetime must be before end datetime"))

        # Check for overlapping time-offs
        if self.id:  # If this is an existing record
            overlaps = DoctorTimeOff.objects.filter(
                doctor=self.doctor
            ).exclude(id=self.id)
        else:  # If this is a new record
            overlaps = DoctorTimeOff.objects.filter(
                doctor=self.doctor
            )

        for overlap in overlaps:
            if (self.start_datetime <= overlap.end_datetime and
                self.end_datetime >= overlap.start_datetime):
                raise ValidationError(_(
                    f"This time off overlaps with {overlap.start_datetime} - {overlap.end_datetime}"
                ))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
