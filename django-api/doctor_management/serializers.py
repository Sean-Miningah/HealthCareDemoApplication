from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from doctor_management.models import DoctorProfile, Specialization, DoctorAvailability, DoctorTimeOff
from accounts.serializers import UserSerializer

User = get_user_model()

class SpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for Specialization model.
    """
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description']


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorAvailability model.
    """
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Validate start_time is before end_time and check for overlaps.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })

        # Doctor and validation for overlaps will be handled in the model's clean method
        return data


class DoctorTimeOffSerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorTimeOff model.
    """
    class Meta:
        model = DoctorTimeOff
        fields = ['id', 'start_datetime', 'end_datetime', 'reason']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Validate start_datetime is before end_datetime.
        """
        if data['start_datetime'] >= data['end_datetime']:
            raise serializers.ValidationError({
                "end_datetime": "End datetime must be after start datetime."
            })

        # Doctor and validation for overlaps will be handled in the model's clean method
        return data


class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorProfile model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    specializations = SpecializationSerializer(source='specialization', many=True, read_only=True)
    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'license_number',
            'specializations', 'years_of_experience', 'biography', 'education',
            'accepting_new_patients', 'consultation_fee', 'address', 'city',
            'state', 'zip_code', 'availabilities'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'user_full_name', 'availabilities']

    def get_user_full_name(self, obj):
        return f"Dr. {obj.user.first_name} {obj.user.last_name}".strip()


class DoctorWithUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new doctor with a user account.
    """
    user = UserSerializer()
    specialization_ids = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        write_only=True, many=True
    )
    availabilities = DoctorAvailabilitySerializer(many=True, required=False)

    class Meta:
        model = DoctorProfile
        fields = [
            'user', 'license_number', 'specialization_ids', 'years_of_experience',
            'biography', 'education', 'accepting_new_patients', 'consultation_fee',
            'address', 'city', 'state', 'zip_code', 'availabilities'
        ]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        specialization_ids = validated_data.pop('specialization_ids', [])
        availabilities_data = validated_data.pop('availabilities', [])

        # Create user with role='DOCTOR'
        user_serializer = UserSerializer(data={**user_data, 'role': 'DOCTOR'})
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Create doctor profile
        doctor_profile = DoctorProfile.objects.create(user=user, **validated_data)

        # Add specializations
        for specialization in specialization_ids:
            doctor_profile.specialization.add(specialization)

        # Create availabilities if provided
        for availability_data in availabilities_data:
            DoctorAvailability.objects.create(
                doctor=doctor_profile,
                **availability_data
            )

        return doctor_profile


class DoctorAvailabilityCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating DoctorAvailability records.
    """
    class Meta:
        model = DoctorAvailability
        fields = ['day_of_week', 'start_time', 'end_time']

    def create(self, validated_data):
        doctor_id = self.context.get('doctor_id')
        if not doctor_id:
            raise serializers.ValidationError("Doctor ID is required")

        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError("Doctor not found")

        return DoctorAvailability.objects.create(doctor=doctor, **validated_data)


class DoctorTimeOffCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating DoctorTimeOff records.
    """
    class Meta:
        model = DoctorTimeOff
        fields = ['start_datetime', 'end_datetime', 'reason']

    def create(self, validated_data):
        doctor_id = self.context.get('doctor_id')
        if not doctor_id:
            raise serializers.ValidationError("Doctor ID is required")

        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError("Doctor not found")

        return DoctorTimeOff.objects.create(doctor=doctor, **validated_data)
