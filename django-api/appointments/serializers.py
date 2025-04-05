from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from appointments.models import Appointment, AppointmentType, AppointmentReminder
from patient_management.models import PatientProfile
from doctor_management.models import DoctorProfile

class AppointmentTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentType model.
    """
    class Meta:
        model = AppointmentType
        fields = ['id', 'name', 'description', 'duration_minutes', 'color_hex']


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentReminder model.
    """
    class Meta:
        model = AppointmentReminder
        fields = ['id', 'reminder_type', 'scheduled_time', 'message', 'sent', 'sent_time', 'appointment']
        read_only_fields = ['id', 'sent', 'sent_time']


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model.
    """
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    appointment_type_name = serializers.CharField(source='appointment_type.name', read_only=True)
    reminders = AppointmentReminderSerializer(many=True, read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'appointment_type', 'appointment_type_name', 'start_datetime',
            'end_datetime', 'status', 'reason', 'notes', 'is_virtual',
            'meeting_link', 'original_appointment', 'reminders',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reminders', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}".strip()

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}".strip()

    def validate(self, data):
        """
        Validate appointment data:
        1. If appointment_type is provided, calculate end_datetime
        2. start_datetime must be in the future (except for admin users)
        """
        # Get the user making the request
        user = self.context['request'].user

        # Calculate end_datetime based on appointment_type if not provided
        if 'appointment_type' in data and 'start_datetime' in data and 'end_datetime' not in data:
            duration = data['appointment_type'].duration_minutes
            data['end_datetime'] = data['start_datetime'] + timezone.timedelta(minutes=duration)

        # Ensure start_datetime is before end_datetime
        if 'start_datetime' in data and 'end_datetime' in data:
            if data['start_datetime'] >= data['end_datetime']:
                raise serializers.ValidationError({
                    "end_datetime": "End time must be after start time."
                })

        # Ensure appointments are not in the past (unless admin)
        if 'start_datetime' in data and not user.is_staff:
            if data['start_datetime'] < timezone.now():
                raise serializers.ValidationError({
                    "start_datetime": "Appointments cannot be scheduled in the past."
                })

        # Other validations (overlaps, doctor availability) are handled in the model's clean method
        return data


class AppointmentCreateSerializer(AppointmentSerializer):
    """
    Serializer for creating a new appointment with reminder options.
    """
    create_reminder = serializers.BooleanField(default=True, write_only=True)
    reminder_hours_before = serializers.IntegerField(default=24, min_value=1, max_value=72, write_only=True)
    reminder_type = serializers.ChoiceField(
        choices=AppointmentReminder.REMINDER_TYPE_CHOICES,
        default='EMAIL',
        write_only=True
    )

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + [
            'create_reminder', 'reminder_hours_before', 'reminder_type'
        ]

    @transaction.atomic
    def create(self, validated_data):
        # Extract reminder data
        create_reminder = validated_data.pop('create_reminder', True)
        reminder_hours_before = validated_data.pop('reminder_hours_before', 24)
        reminder_type = validated_data.pop('reminder_type', 'EMAIL')

        # Create the appointment
        appointment = super().create(validated_data)

        # Create a reminder if requested
        if create_reminder and appointment.start_datetime:
            reminder_time = appointment.start_datetime - timezone.timedelta(hours=reminder_hours_before)

            # Don't create reminder if it would be in the past
            if reminder_time > timezone.now():
                AppointmentReminder.objects.create(
                    appointment=appointment,
                    reminder_type=reminder_type,
                    scheduled_time=reminder_time,
                    message=f"Reminder: You have an appointment with {appointment.doctor} on {appointment.start_datetime.strftime('%Y-%m-%d at %H:%M')}"
                )

        return appointment


class AppointmentUpdateSerializer(AppointmentSerializer):
    """
    Serializer for updating an appointment.
    """
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields

    def validate_status(self, value):
        """
        Validate status transitions:
        - Only doctors/staff can mark as COMPLETED
        - Only patients can mark as CANCELLED
        - Status shouldn't go backward
        """
        user = self.context['request'].user
        instance = self.instance

        # Define status progression order
        status_order = {
            'SCHEDULED': 1,
            'CONFIRMED': 2,
            'CHECKED_IN': 3,
            'IN_PROGRESS': 4,
            'COMPLETED': 5,
            'CANCELLED': 6,
            'NO_SHOW': 6,
            'RESCHEDULED': 6
        }

        # Check if trying to downgrade status
        if instance and status_order.get(value, 0) < status_order.get(instance.status, 0):
            raise serializers.ValidationError("Cannot change to a previous status.")

        # Only doctors/staff can mark as completed
        if value == 'COMPLETED' and not (hasattr(user, 'doctorprofile') or user.is_staff):
            raise serializers.ValidationError("Only doctors or staff can mark appointments as completed.")

        # Only allow patients to cancel their own appointments
        if value == 'CANCELLED' and not (hasattr(user, 'patientprofile') or user.is_staff):
            if not hasattr(user, 'patient') or (instance and instance.patient.user != user):
                raise serializers.ValidationError("Only patients can cancel their own appointments.")

        return value


class AppointmentRescheduleSerializer(serializers.Serializer):
    """
    Serializer for rescheduling an appointment.
    """
    new_start_datetime = serializers.DateTimeField()
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_new_start_datetime(self, value):
        """
        Validate new appointment time is in the future.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("New appointment time must be in the future.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Reschedule an appointment by creating a new one and updating the status of the old one.
        """
        new_start_datetime = validated_data.get('new_start_datetime')
        reason = validated_data.get('reason', '')

        # Calculate the duration of the original appointment
        duration = (instance.end_datetime - instance.start_datetime).total_seconds() // 60
        new_end_datetime = new_start_datetime + timezone.timedelta(minutes=int(duration))

        # Update the status of the original appointment
        instance.status = 'RESCHEDULED'
        instance.notes += f"\nRescheduled on {timezone.now().strftime('%Y-%m-%d %H:%M')} to {new_start_datetime.strftime('%Y-%m-%d %H:%M')}. Reason: {reason}"
        instance.save()

        # Create a new appointment
        new_appointment = Appointment.objects.create(
            patient=instance.patient,
            doctor=instance.doctor,
            appointment_type=instance.appointment_type,
            start_datetime=new_start_datetime,
            end_datetime=new_end_datetime,
            status='SCHEDULED',
            reason=instance.reason,
            notes=f"Rescheduled from appointment on {instance.start_datetime.strftime('%Y-%m-%d %H:%M')}. {reason}",
            is_virtual=instance.is_virtual,
            meeting_link=instance.meeting_link,
            original_appointment=instance
        )

        # Create a new reminder for the new appointment
        reminder_time = new_start_datetime - timezone.timedelta(hours=24)
        if reminder_time > timezone.now():
            AppointmentReminder.objects.create(
                appointment=new_appointment,
                reminder_type='EMAIL',
                scheduled_time=reminder_time,
                message=f"Reminder: You have a rescheduled appointment with {new_appointment.doctor} on {new_start_datetime.strftime('%Y-%m-%d at %H:%M')}"
            )

        return new_appointment


class DoctorAvailabilitySlotSerializer(serializers.Serializer):
    """
    Serializer for available appointment slots.
    """
    date = serializers.DateField()
    doctor_id = serializers.UUIDField()

    def validate(self, data):
        """
        Validate the doctor exists.
        """
        try:
            data['doctor'] = DoctorProfile.objects.get(id=data['doctor_id'])
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError({"doctor_id": "Doctor not found."})

        return data