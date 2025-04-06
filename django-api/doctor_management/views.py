from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from doctor_management.models import DoctorProfile, Specialization, DoctorAvailability, DoctorTimeOff
from doctor_management.serializers import (
    DoctorProfileSerializer, DoctorWithUserSerializer,
    SpecializationSerializer, DoctorAvailabilitySerializer,
    DoctorTimeOffSerializer, DoctorAvailabilityCreateUpdateSerializer,
    DoctorTimeOffCreateUpdateSerializer
)
from accounts.permissions import IsAdminUser, IsDoctor

class SpecializationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing medical specializations.
    """
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer

    def get_permissions(self):
        """
        - Allow anyone to view specializations
        - Only admin can create, update, or delete
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class DoctorProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing doctor profiles.
    """
    queryset = DoctorProfile.objects.all()

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return DoctorWithUserSerializer
        return DoctorProfileSerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Doctors can only view and update their own profile
        - Anyone can view the list of doctors and their details
        - Only admin can create a new doctor profile
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsDoctor| IsAdminUser]
        elif self.action in ['add_availability', 'add_time_off']:
            permission_classes = [IsDoctor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        - Anyone can see the list of doctors
        - For update/delete, doctors can only modify their own data
        """
        user = self.request.user
        queryset = DoctorProfile.objects.all()

        # If this is not a list/retrieve action, restrict to own profile
        if self.action not in ['list', 'retrieve'] and not user.is_staff:
            if hasattr(user, 'doctorprofile'):
                return queryset.filter(user=user)
            return DoctorProfile.objects.none()

        # For list action, add filtering options
        if self.action == 'list':
            # Filter by specialization
            specialization_id = self.request.query_params.get('specialization')
            if specialization_id:
                queryset = queryset.filter(specialization__id=specialization_id)

            # Filter by accepting new patients
            accepting_new = self.request.query_params.get('accepting_new_patients')
            if accepting_new and accepting_new.lower() == 'true':
                queryset = queryset.filter(accepting_new_patients=True)
        if self.action in ['update', 'partial_update', 'destroy']:
            id = self.kwargs.get('id')
            return self.kwargs.get(id=id)
        return queryset

    def perform_update(self, serializer):
        """
        Check permissions before updating.
        """
        doctorprofile = self.get_object()
        user = self.request.user

        print(f"here we are performing a update with {user}")
        # Only the doctor or admin can update
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != doctorprofile):
            self.permission_denied(
                self.request,
                message="You do not have permission to modify this availability."
            )

        serializer.save()

    def perform_partial_update(self, serializer):
        """
        Check permission before making partial update.
        """
        doctorprofile = self.get_object()
        user = self.request.user

        print(f"here we are performing a partial update with {user}")

        # Only the doctor or admin can update
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != doctorprofile):
            self.permission_denied(
                self.request,
                message="You do not have permission to modify this availability."
            )

        serializer.save()

    @action(detail=False, methods=['get'], permission_classes=[IsDoctor])
    def me(self, request):
        """
        API endpoint for getting the current user's doctor profile.
        """
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        serializer = DoctorProfileSerializer(doctor)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def availabilities(self, request, pk=None):
        """
        API endpoint for listing a doctor's availability.
        """
        doctor = self.get_object()
        availabilities = doctor.availabilities.all()
        serializer = DoctorAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_availability(self, request, pk=None):
        """
        API endpoint for adding availability to a doctor.
        """
        doctor = self.get_object()

        # Check if the user has permission to add availability
        user = request.user
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != doctor):
            return Response(
                {'detail': 'You do not have permission to modify this doctor\'s availability.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DoctorAvailabilityCreateUpdateSerializer(
            data=request.data,
            context={'doctor_id': doctor.id}
        )
        serializer.is_valid(raise_exception=True)
        availability = serializer.save()

        return Response(
            DoctorAvailabilitySerializer(availability).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def time_offs(self, request, pk=None):
        """
        API endpoint for listing a doctor's time off records.
        """
        doctor = self.get_object()

        # Only show future time offs for regular users
        if not request.user.is_staff and (not hasattr(request.user, 'doctorprofile') or request.user.doctorpofile != doctor):
            time_offs = doctor.time_offs.filter(start_datetime__gte=timezone.now())
        else:
            time_offs = doctor.time_offs.all()

        serializer = DoctorTimeOffSerializer(time_offs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_time_off(self, request, pk=None):
        """
        API endpoint for adding time off for a doctor.
        """
        doctor = self.get_object()

        # Check if the user has permission to add time off
        user = request.user
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != doctor):
            return Response(
                {'detail': 'You do not have permission to modify this doctor\'s schedule.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DoctorTimeOffCreateUpdateSerializer(
            data=request.data,
            context={'doctor_id': doctor.id}
        )
        serializer.is_valid(raise_exception=True)
        time_off = serializer.save()

        return Response(
            DoctorTimeOffSerializer(time_off).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        """
        API endpoint for getting available appointment slots for a specific date.
        """
        doctor = self.get_object()
        date_str = request.query_params.get('date')

        if not date_str:
            return Response(
                {'detail': 'Date parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Parse the date string
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Get day of week (0=Monday, 6=Sunday)
            day_of_week = date.weekday()

            # Get availabilities for that day
            availabilities = doctor.availabilities.filter(day_of_week=day_of_week)

            if not availabilities.exists():
                return Response([])  # No availability on this day

            # Get appointment duration (default to 30 minutes)
            duration_minutes = int(request.query_params.get('duration', 30))

            # Get existing appointments for that day
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())

            from appointments.models import Appointment
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                start_datetime__gte=start_datetime,
                start_datetime__lt=end_datetime,
                status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS']
            )

            # Get time offs for that day
            time_offs = doctor.time_offs.filter(
                start_datetime__lt=end_datetime,
                end_datetime__gt=start_datetime
            )

            # Generate available slots
            available_slots = []

            for availability in availabilities:
                # Convert availability times to datetime objects for this date
                start_time = datetime.combine(date, availability.start_time)
                end_time = datetime.combine(date, availability.end_time)

                # Generate potential slots
                current_slot = start_time
                while current_slot + timedelta(minutes=duration_minutes) <= end_time:
                    slot_end = current_slot + timedelta(minutes=duration_minutes)

                    # Check if slot overlaps with existing appointments
                    is_available = True

                    # Check against existing appointments
                    for appointment in existing_appointments:
                        if (current_slot < appointment.end_datetime and
                            slot_end > appointment.start_datetime):
                            is_available = False
                            break

                    # Check against time offs
                    if is_available:
                        for time_off in time_offs:
                            if (current_slot < time_off.end_datetime and
                                slot_end > time_off.start_datetime):
                                is_available = False
                                break

                    # Add to available slots if not overlapping
                    if is_available:
                        available_slots.append({
                            'start_time': current_slot.strftime('%H:%M'),
                            'end_time': slot_end.strftime('%H:%M'),
                        })

                    # Move to next slot
                    current_slot += timedelta(minutes=duration_minutes)

            return Response(available_slots)

        except ValueError:
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing doctor availability.
    """
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Doctors can only modify their own availability
        - Anyone can view availability
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter availabilities based on user permissions.
        """
        user = self.request.user

        # If admin, can see all
        if user.is_staff:
            return DoctorAvailability.objects.all()

        # If doctor, can only see own availabilities
        if hasattr(user, 'doctorprofile'):
            return DoctorAvailability.objects.filter(doctor=user.doctorprofile)

        # For other users (patients), filter by requested doctor
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            return DoctorAvailability.objects.filter(doctor__id=doctor_id)

        # Default: no access
        return DoctorAvailability.objects.none()


    def perform_update(self, serializer):
        """
        Check permissions before updating.
        """
        availability = self.get_object()
        user = self.request.user

        # Only the doctor or admin can update
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != availability.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to modify this availability."
            )

        serializer.save()

    def perform_destroy(self, instance):
        """
        Check permissions before deleting.
        """
        user = self.request.user

        # Only the doctor or admin can delete
        if not user.is_staff and (not hasattr(user, 'doctor') or user.doctor != instance.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to delete this availability."
            )

        instance.delete()


class DoctorTimeOffViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing doctor time off.
    """
    queryset = DoctorTimeOff.objects.all()
    serializer_class = DoctorTimeOffSerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Doctors can only modify their own time off
        - Anyone can view time off
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter time offs based on user permissions.
        """
        user = self.request.user

        # If admin, can see all
        if user.is_staff:
            return DoctorTimeOff.objects.all()

        # If doctor, can only see own time offs
        if hasattr(user, 'doctorprofile'):
            return DoctorTimeOff.objects.filter(doctor=user.doctorprofile)

        # For other users (patients), filter by requested doctor and only future
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            return DoctorTimeOff.objects.filter(
                doctor__id=doctor_id,
                start_datetime__gte=timezone.now()
            )

        # Default: no access
        return DoctorTimeOff.objects.none()

    def perform_update(self, serializer):
        """
        Check permissions before updating.
        """
        time_off = self.get_object()
        user = self.request.user

        # Only the doctor or admin can update
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != time_off.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to modify this time off."
            )

        serializer.save()

    def perform_destroy(self, instance):
        """
        Check permissions before deleting.
        """
        user = self.request.user

        # Only the doctor or admin can delete
        if not user.is_staff and (not hasattr(user, 'doctorprofile') or user.doctorprofile != instance.doctor):
            self.permission_denied(
                self.request,
                message="You do not have permission to delete this time off."
            )

        instance.delete()
