from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from medical_records.models import MedicalRecord, MedicalImage, MedicalRecordAccess
from medical_records.serializers import (
    MedicalRecordSerializer, MedicalImageSerializer,
    MedicalRecordAccessSerializer, MedicalRecordCreateSerializer,
    MedicalRecordUpdateSerializer, MedicalImageCreateSerializer
)
from accounts.permissions import IsAdminUser, IsDoctor, IsPatient


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing medical records.
    """
    queryset = MedicalRecord.objects.all()

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return MedicalRecordCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MedicalRecordUpdateSerializer
        return MedicalRecordSerializer

    def get_permissions(self):
        """
        - Admin and doctors can create/update records
        - Patients can only view their own records
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter medical records based on user role:
        - Admin can see all records
        - Doctors can see records for their patients
        - Patients can only see their own records
        """
        user = self.request.user
        queryset = MedicalRecord.objects.all()

        # Admin can see all
        if user.is_staff:
            pass
        # Doctors can see records for their patients or records they created
        elif hasattr(user, 'doctor'):
            queryset = queryset.filter(
                Q(doctor=user.doctor) |
                Q(patient__appointments__doctor=user.doctor)
            ).distinct()
        # Patients can only see their own records
        elif hasattr(user, 'patient'):
            queryset = queryset.filter(patient=user.patient)

            # Filter out confidential records that need doctor explanation
            confidential_filter = self.request.query_params.get('include_confidential')
            if not confidential_filter or confidential_filter.lower() != 'true':
                queryset = queryset.filter(is_confidential=False)
        # Other users can't see any records
        else:
            return MedicalRecord.objects.none()

        # Apply filters from query parameters
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor__id=doctor_id)

        patient_id = self.request.query_params.get('patient')
        if patient_id and (user.is_staff or hasattr(user, 'doctor')):
            queryset = queryset.filter(patient__id=patient_id)

        appointment_id = self.request.query_params.get('appointment')
        if appointment_id:
            queryset = queryset.filter(appointment__id=appointment_id)

        # Date range filters
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """
        Create a medical record and check permissions.
        """
        user = self.request.user

        # Only doctors and admins can create medical records
        if not user.is_staff and not hasattr(user, 'doctor'):
            self.permission_denied(
                self.request,
                message="Only doctors and administrators can create medical records."
            )

        # If user is a doctor, set the doctor field to the user's doctor profile
        if hasattr(user, 'doctor') and 'doctor' not in serializer.validated_data:
            serializer.validated_data['doctor'] = user.doctor

        # Create the record and log the access
        record = serializer.save()

        # Access logging is handled in the serializer
        return record

    def perform_update(self, serializer):
        """
        Update a medical record and check permissions.
        """
        record = self.get_object()
        user = self.request.user

        # Only the doctor who created the record or admin can update
        if not user.is_staff and not (hasattr(user, 'doctor') and record.doctor == user.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to update this medical record."
            )

        # Update the record and log the access
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a medical record and log the access.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Log the access
        user = request.user
        client_ip = request.META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=instance,
            user=user,
            ip_address=client_ip,
            access_reason="Viewed medical record"
        )

        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsPatient])
    def my_records(self, request):
        """
        API endpoint for patients to get their own medical records.
        """
        user = request.user

        if not hasattr(user, 'patient'):
            return Response(
                {'detail': 'You must be a patient to access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Apply filters
        queryset = MedicalRecord.objects.filter(patient=user.patient)

        # Filter out confidential records that need doctor explanation
        include_confidential = request.query_params.get('include_confidential')
        if not include_confidential or include_confidential.lower() != 'true':
            queryset = queryset.filter(is_confidential=False)

        # Date range
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        queryset = queryset.order_by('-created_at')
        serializer = MedicalRecordSerializer(queryset, many=True)

        # Log this access
        client_ip = request.META.get('REMOTE_ADDR', None)
        for record in queryset:
            MedicalRecordAccess.objects.create(
                medical_record=record,
                user=user,
                ip_address=client_ip,
                access_reason="Viewed in 'my records' list"
            )

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def access_logs(self, request, pk=None):
        """
        API endpoint for viewing access logs for a medical record.
        """
        record = self.get_object()
        user = request.user

        # Only the doctor who created the record, the patient, or admin can view logs
        if not user.is_staff and not (
            (hasattr(user, 'doctor') and record.doctor == user.doctor) or
            (hasattr(user, 'patient') and record.patient == user.patient)
        ):
            return Response(
                {'detail': 'You do not have permission to view access logs for this record.'},
                status=status.HTTP_403_FORBIDDEN
            )

        access_logs = record.access_logs.all().order_by('-accessed_at')
        serializer = MedicalRecordAccessSerializer(access_logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """
        API endpoint for adding an image to a medical record.
        """
        record = self.get_object()
        user = request.user

        # Only the doctor who created the record or admin can add images
        if not user.is_staff and not (hasattr(user, 'doctor') and record.doctor == user.doctor):
            return Response(
                {'detail': 'You do not have permission to add images to this record.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MedicalImageCreateSerializer(
            data=request.data,
            context={'medical_record_id': record.id, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        image = serializer.save()

        return Response(
            MedicalImageSerializer(image).data,
            status=status.HTTP_201_CREATED
        )


class MedicalImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing medical images.
    """
    queryset = MedicalImage.objects.all()
    serializer_class = MedicalImageSerializer

    def get_permissions(self):
        """
        - Admin and doctors can create/update/delete images
        - Patients can only view their own images
        """
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter images based on user role.
        """
        user = self.request.user

        # Admin can see all
        if user.is_staff:
            return MedicalImage.objects.all()

        # Doctors can see images for their patients or for records they created
        elif hasattr(user, 'doctor'):
            return MedicalImage.objects.filter(
                Q(medical_record__doctor=user.doctor) |
                Q(medical_record__patient__appointments__doctor=user.doctor)
            ).distinct()

        # Patients can only see their own images
        elif hasattr(user, 'patient'):
            # Don't show images from confidential records
            return MedicalImage.objects.filter(
                medical_record__patient=user.patient,
                medical_record__is_confidential=False
            )

        # Other users can't see any images
        return MedicalImage.objects.none()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a medical image and log the access.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Log the access to the parent medical record
        user = request.user
        client_ip = request.META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=instance.medical_record,
            user=user,
            ip_address=client_ip,
            access_reason="Viewed medical image"
        )

        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Create a medical image and check permissions.
        """
        medical_record_id = serializer.validated_data.get('medical_record').id
        medical_record = get_object_or_404(MedicalRecord, id=medical_record_id)

        user = self.request.user

        # Only the doctor who created the record or admin can add images
        if not user.is_staff and not (hasattr(user, 'doctor') and medical_record.doctor == user.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to add images to this record."
            )

        # Log the access
        client_ip = self.request.META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=medical_record,
            user=user,
            ip_address=client_ip,
            access_reason="Added image to medical record"
        )

        serializer.save()

    def perform_update(self, serializer):
        """
        Update a medical image and check permissions.
        """
        image = self.get_object()
        user = self.request.user

        # Only the doctor who created the record or admin can update images
        if not user.is_staff and not (hasattr(user, 'doctor') and image.medical_record.doctor == user.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to update this image."
            )

        # Log the access
        client_ip = self.request.META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=image.medical_record,
            user=user,
            ip_address=client_ip,
            access_reason="Updated medical image"
        )

        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a medical image and check permissions.
        """
        user = self.request.user

        # Only the doctor who created the record or admin can delete images
        if not user.is_staff and not (hasattr(user, 'doctor') and instance.medical_record.doctor == user.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to delete this image."
            )

        # Log the access
        client_ip = self.request.META.get('REMOTE_ADDR', None)

        MedicalRecordAccess.objects.create(
            medical_record=instance.medical_record,
            user=user,
            ip_address=client_ip,
            access_reason="Deleted medical image"
        )

        instance.delete()


class MedicalRecordAccessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing medical record access logs.
    Read-only to prevent modification of the audit trail.
    """
    queryset = MedicalRecordAccess.objects.all()
    serializer_class = MedicalRecordAccessSerializer

    def get_permissions(self):
        """
        - Admin can see all access logs
        - Doctors can see logs for records they created
        - Patients can see logs for their own records
        """
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter access logs based on user role.
        """
        user = self.request.user

        # Admin can see all
        if user.is_staff:
            return MedicalRecordAccess.objects.all()

        # Doctors can see logs for records they created
        elif hasattr(user, 'doctor'):
            return MedicalRecordAccess.objects.filter(
                medical_record__doctor=user.doctor
            )

        # Patients can see logs for their own records
        elif hasattr(user, 'patient'):
            return MedicalRecordAccess.objects.filter(
                medical_record__patient=user.patient
            )

        # Other users can't see any logs
        return MedicalRecordAccess.objects.none()