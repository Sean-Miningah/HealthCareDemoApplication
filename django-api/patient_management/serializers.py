from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from patient_management.models import PatientProfile, InsuranceProvider, PatientInsurance
from accounts.serializers import UserSerializer

User = get_user_model()

class InsuranceProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for InsuranceProvider model.
    """
    class Meta:
        model = InsuranceProvider
        fields = ['id', 'name', 'contact_number', 'contact_email']


class PatientInsuranceSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientInsurance model.
    """
    insurance_provider_name = serializers.CharField(source='insurance_provider.name', read_only=True)

    class Meta:
        model = PatientInsurance
        fields = [
            'id', 'insurance_provider', 'insurance_provider_name',
            'policy_number', 'group_number', 'policy_holder_name',
            'policy_holder_relation', 'start_date', 'end_date', 'is_primary'
        ]


class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientProfile model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    insurances = PatientInsuranceSerializer(many=True, read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'date_of_birth',
            'gender', 'blood_type', 'allergies', 'address', 'city', 'state',
            'zip_code', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'medical_conditions',
            'current_medications', 'insurances'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'user_full_name', 'insurances']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class PatientWithUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new patient with a user account.
    """
    user = UserSerializer()
    insurances = PatientInsuranceSerializer(many=True, required=False)

    class Meta:
        model = PatientProfile
        fields = [
            'user', 'date_of_birth', 'gender', 'blood_type', 'allergies',
            'address', 'city', 'state', 'zip_code', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'medical_conditions', 'current_medications', 'insurances'
        ]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        insurances_data = validated_data.pop('insurances', [])

        # Create user with role='PATIENT'
        user_serializer = UserSerializer(data={**user_data, 'role': 'PATIENT'})
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Create patient profile
        patient_profile = PatientProfile.objects.create(user=user, **validated_data)

        # Create insurance records if provided
        for insurance_data in insurances_data:
            insurance_provider = insurance_data.pop('insurance_provider')
            PatientInsurance.objects.create(
                patient=patient_profile,
                insurance_provider=insurance_provider,
                **insurance_data
            )

        return patient_profile


class PatientInsuranceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating PatientInsurance records.
    """
    class Meta:
        model = PatientInsurance
        fields = [
            'insurance_provider', 'policy_number', 'group_number',
            'policy_holder_name', 'policy_holder_relation', 'start_date',
            'end_date', 'is_primary'
        ]

    def create(self, validated_data):
        patient_id = self.context.get('patient_id')
        if not patient_id:
            raise serializers.ValidationError("Patient ID is required")

        try:
            patient = PatientProfile.objects.get(id=patient_id)
        except PatientProfile.DoesNotExist:
            raise serializers.ValidationError("Patient not found")

        return PatientInsurance.objects.create(patient=patient, **validated_data)