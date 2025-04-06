from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from medical_records.models import MedicalRecord, MedicalImage, MedicalRecordAccess
from appointments.models import Appointment


class MedicalImageSerializer(serializers.ModelSerializer):
    """
    Serializer for MedicalImage model.
    """
    class Meta:
        model = MedicalImage
        fields = ['id', 'title', 'description', 'image_file', 'image_type', 'created_at', 'medical_record']
        read_only_fields = ['id', 'created_at']


class MedicalRecordAccessSerializer(serializers.ModelSerializer):
    """
    Serializer for MedicalRecordAccess model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecordAccess
        fields = ['id', 'user', 'user_email', 'user_name', 'accessed_at', 'access_reason', 'ip_address']
        read_only_fields = ['id', 'user', 'user_email', 'user_name', 'accessed_at', 'ip_address']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

class MedicalImageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updateing MedicalImage model.
    """
    image_file = serializers.FileField(required=False)
    class Meta:
        model = MedicalImage
        fields = ['id', 'title', 'description', 'image_file', 'image_type', 'created_at', 'medical_record']
        read_only_fields = ['id', 'created_at', 'medical_record']



class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for MedicalRecord model.
    """
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField(required=False)
    images = MedicalImageSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'appointment', 'appointment_date', 'diagnosis', 'treatment_plan',
            'prescription', 'notes', 'temperature', 'blood_pressure_systolic',
            'blood_pressure_diastolic', 'pulse_rate', 'respiratory_rate',
            'weight', 'height', 'is_confidential', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient_name', 'doctor_name',
                           'appointment_date', 'images', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}".strip()

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}".strip()

    def get_appointment_date(self, obj):
        if obj.appointment:
            return obj.appointment.start_datetime
        return None

    def validate(self, data):
        """
        Validate the medical record:
        1. If appointment is provided, check that doctor and patient match
        """
        if 'appointment' in data:
            appointment = data['appointment']

            # If patient is in the data, check it matches appointment
            if 'patient' in data and data['patient'] != appointment.patient:
                raise serializers.ValidationError({
                    "patient": "Patient must match the patient from the appointment."
                })
            else:
                # Set patient from appointment if not provided
                data['patient'] = appointment.patient

            # If doctor is in the data, check it matches appointment
            if 'doctor' in data and data['doctor'] != appointment.doctor:
                raise serializers.ValidationError({
                    "doctor": "Doctor must match the doctor from the appointment."
                })
            else:
                # Set doctor from appointment if not provided
                data['doctor'] = appointment.doctor

        return data

    def create(self, validated_data):
        """
        Create a medical record and log the access.
        """
        record = super().create(validated_data)

        # Log the access
        user = self.context['request'].user
        client_ip = self.context['request'].META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=record,
            user=user,
            ip_address=client_ip,
            access_reason="Created medical record"
        )

        return record


class MedicalRecordCreateSerializer(MedicalRecordSerializer):
    """
    Serializer for creating a medical record with images.
    """
    images = MedicalImageSerializer(many=True, required=False)

    class Meta(MedicalRecordSerializer.Meta):
        fields = MedicalRecordSerializer.Meta.fields

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])

        # Create the medical record
        medical_record = super().create(validated_data)

        # Create medical images
        for image_data in images_data:
            MedicalImage.objects.create(medical_record=medical_record, **image_data)

        return medical_record


class MedicalRecordUpdateSerializer(MedicalRecordSerializer):
    """
    Serializer for updating a medical record.
    """
    class Meta(MedicalRecordSerializer.Meta):
        fields = MedicalRecordSerializer.Meta.fields

    def update(self, instance, validated_data):
        """
        Update a medical record and log the access.
        """
        record = super().update(instance, validated_data)

        # Log the access
        user = self.context['request'].user
        client_ip = self.context['request'].META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=record,
            user=user,
            ip_address=client_ip,
            access_reason="Updated medical record"
        )

        return record


class MedicalImageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding an image to a medical record.
    """
    class Meta:
        model = MedicalImage
        fields = ['title', 'description', 'image_file', 'image_type']

    def create(self, validated_data):
        medical_record_id = self.context.get('medical_record_id')
        if not medical_record_id:
            raise serializers.ValidationError("Medical record ID is required")

        try:
            medical_record = MedicalRecord.objects.get(id=medical_record_id)
        except MedicalRecord.DoesNotExist:
            raise serializers.ValidationError("Medical record not found")

        # Log the access
        user = self.context['request'].user
        client_ip = self.context['request'].META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=medical_record,
            user=user,
            ip_address=client_ip,
            access_reason="Added image to medical record"
        )

        return MedicalImage.objects.create(medical_record=medical_record, **validated_data)
