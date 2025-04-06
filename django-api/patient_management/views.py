from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from patient_management.models import PatientProfile, InsuranceProvider, PatientInsurance
from patient_management.serializers import (
    PatientProfileSerializer, PatientWithUserSerializer,
    InsuranceProviderSerializer, PatientInsuranceSerializer,
    PatientInsuranceCreateUpdateSerializer
)
from accounts.permissions import IsAdminUser, IsPatient

class InsuranceProviderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing insurance providers.
    """
    queryset = InsuranceProvider.objects.all()
    serializer_class = InsuranceProviderSerializer

    def get_permissions(self):
        """
        - Allow anyone to view insurance providers
        - Only admin can create, update, or delete
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class PatientProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing patient profiles.
    """
    queryset = PatientProfile.objects.all()

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return PatientWithUserSerializer
        return PatientProfileSerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Patients can only view and update their own profile
        - Anyone can create a new patient profile (registration)
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Regular users can only see their own data.
        Admins and staff can see all patients.
        """
        user = self.request.user
        if user.is_staff:
            return PatientProfile.objects.all()

        # If the user is a patient, they can only see their own profile
        if hasattr(user, 'patientprofile'):
            return PatientProfile.objects.filter(user=user)

        # Other users (like doctors) can't see patient profiles
        return PatientProfile.objects.none()

    @action(detail=False, methods=['get'], permission_classes=[IsPatient])
    def me(self, request):
        """
        API endpoint for getting the current user's patient profile.
        """
        patient = get_object_or_404(PatientProfile, user=request.user)
        serializer = PatientProfileSerializer(patient)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def insurances(self, request, pk=None):
        """
        API endpoint for listing a patient's insurance records.
        """
        patient = self.get_object()

        # Check if the user has permission to view this patient's insurance
        user = request.user
        if not user.is_staff and (not hasattr(user, 'patientprofile') or user.patientprofile != patient):
            return Response(
                {'detail': 'You do not have permission to view this information.'},
                status=status.HTTP_403_FORBIDDEN
            )

        insurances = patient.insurances.all()
        serializer = PatientInsuranceSerializer(insurances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_insurance(self, request, pk=None):
        """
        API endpoint for adding insurance to a patient.
        """
        patient = self.get_object()

        # Check if the user has permission to add insurance to this patient
        user = request.user
        if not user.is_staff and (not hasattr(user, 'patientprofile') or user.patientprofile != patient):
            return Response(
                {'detail': 'You do not have permission to add insurance to this patient.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PatientInsuranceCreateUpdateSerializer(
            data=request.data,
            context={'patient_id': patient.id}
        )
        serializer.is_valid(raise_exception=True)
        insurance = serializer.save()

        # If this insurance is marked as primary, make sure others are not
        if insurance.is_primary:
            patient.insurances.exclude(id=insurance.id).filter(is_primary=True).update(is_primary=False)

        return Response(
            PatientInsuranceSerializer(insurance).data,
            status=status.HTTP_201_CREATED
        )


class PatientInsuranceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing patient insurance records.
    """
    queryset = PatientInsurance.objects.all()
    serializer_class = PatientInsuranceSerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Patients can only view and update their own insurance
        """
        if self.action in ['list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Regular users can only see their own insurance.
        Admins can see all insurance records.
        """
        user = self.request.user
        if user.is_staff:
            return PatientInsurance.objects.all()

        # If the user is a patient, they can only see their own insurance
        if hasattr(user, 'patientprofile'):
            return PatientInsurance.objects.filter(patient=user.patientprofile)

        # Other users can't see insurance records
        return PatientInsurance.objects.none()

    def perform_update(self, serializer):
        """
        When updating insurance, handle the primary flag.
        """
        with transaction.atomic():
            insurance = serializer.save()

            # If this insurance is marked as primary, make sure others are not
            if insurance.is_primary:
                insurance.patient.insurances.exclude(id=insurance.id).filter(is_primary=True).update(is_primary=False)

    def perform_destroy(self, instance):
        """
        When deleting insurance, check if it's the last one.
        """
        patient = instance.patient

        # If this is the only insurance, we might want to prevent deletion
        # or allow it with a warning
        if patient.insurances.count() == 1:
            # For now, we're allowing it but you might want to add logging or notifications
            pass

        # If this was the primary insurance, set another one as primary
        if instance.is_primary and patient.insurances.exclude(id=instance.id).exists():
            # Get another insurance to make primary
            new_primary = patient.insurances.exclude(id=instance.id).first()
            new_primary.is_primary = True
            new_primary.save()

        instance.delete()