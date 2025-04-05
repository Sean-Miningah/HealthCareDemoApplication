from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from appointments.models import Appointment, AppointmentType, AppointmentReminder
from appointments.serializers import (
    AppointmentSerializer, AppointmentTypeSerializer,
    AppointmentReminderSerializer, AppointmentCreateSerializer,
    AppointmentUpdateSerializer, AppointmentRescheduleSerializer
)
from accounts.permissions import IsAdminUser, IsDoctor, IsPatient


class AppointmentTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointment types.
    """
    queryset = AppointmentType.objects.all()
    serializer_class = AppointmentTypeSerializer

    def get_permissions(self):
        """
        - Anyone can view appointment types
        - Only admin can create, update, or delete
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointments.
    """
    queryset = Appointment.objects.all()

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AppointmentUpdateSerializer
        elif self.action == 'reschedule':
            return AppointmentRescheduleSerializer
        return AppointmentSerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Doctors and patients have limited access
        """
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter appointments based on user role:
        - Admin/staff can see all appointments
        - Doctors can see their own appointments
        - Patients can see their own appointments
        """
        user = self.request.user
        queryset = Appointment.objects.all()

        # Admin/staff can see all
        if user.is_staff:
            pass
        # Doctors can see their appointments
        elif user.role == 'DOCTOR' and hasattr(user, 'doctorprofile'):
            queryset = queryset.filter(doctor=user.doctorprofile)
        # Patients can see their appointments
        elif user.role == 'PATIENT' and hasattr(user, 'patientprofile'):
            queryset = queryset.filter(patient=user.patientprofile)
        # Other users can't see any appointments
        else:
            return Appointment.objects.none()

        # Apply filters from query parameters
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor__id=doctor_id)

        patient_id = self.request.query_params.get('patient')
        if patient_id and (user.is_staff or user.role == 'DOCTOR'):  # Only staff/doctors can filter by patient
            queryset = queryset.filter(patient__id=patient_id)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Date range filters
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(start_datetime__date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(start_datetime__date__lte=end_date)

        # Upcoming appointments
        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() == 'true':
            queryset = queryset.filter(
                start_datetime__gte=timezone.now(),
                status__in=['SCHEDULED', 'CONFIRMED']
            )

        # Past appointments
        past = self.request.query_params.get('past')
        if past and past.lower() == 'true':
            queryset = queryset.filter(
                Q(start_datetime__lt=timezone.now()) |
                Q(status__in=['COMPLETED', 'CANCELLED', 'NO_SHOW', 'RESCHEDULED'])
            )

        return queryset.order_by('start_datetime')

    def perform_create(self, serializer):
        """
        Create an appointment and check user permissions.
        """
        user = self.request.user

        # Prepare additional data to pass to serializer's save method
        additional_data = {}

        # Set the patient to the current user if not provided and user is a patient
        if hasattr(user, 'patient') and 'patient' not in serializer.validated_data:
            additional_data['patient'] = user.patient

        # If the user is not admin/staff, validate they can only make appointments for themselves
        if not user.is_staff and hasattr(user, 'patient'):
            patient_in_data = serializer.validated_data.get('patient', user.patient)
            if patient_in_data != user.patient:
                self.permission_denied(
                    self.request,
                    message="You can only make appointments for yourself."
                )

        # Save with any additional data
        serializer.save(**additional_data)

    def perform_update(self, serializer):
        """
        Update an appointment and check user permissions.
        """
        appointment = self.get_object()
        user = self.request.user

        # Check permissions based on status change
        new_status = serializer.validated_data.get('status')

        # Only doctors/staff can mark as CHECKED_IN, IN_PROGRESS, COMPLETED, or NO_SHOW
        if new_status in ['CHECKED_IN', 'IN_PROGRESS', 'COMPLETED', 'NO_SHOW']:
            if not user.is_staff and not hasattr(user, 'doctorprofile'):
                self.permission_denied(
                    self.request,
                    message="You do not have permission to update to this status."
                )

        # Only patients can CANCEL their own appointments
        if new_status == 'CANCELLED' and not user.is_staff:
            print("The user here is", user)
            if not hasattr(user, 'patientprofile') or appointment.patient != user.patientprofile:
                self.permission_denied(
                    self.request,
                    message="You can only cancel your own appointments."
                )

        serializer.save()

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """
        API endpoint for rescheduling an appointment.
        """
        try:
            appointment = self.get_object()
            user = request.user

            # Check permissions - only the patient, doctor, or admin can reschedule
            if not user.is_staff and not (
                (user.role == 'PATIENT' and hasattr(user, 'patientprofile') and appointment.patient == user.patientprofile) or
                (user.role == 'DOCTOR' and hasattr(user, 'doctorprofile') and appointment.doctor == user.doctorprofile)
            ):
                return Response(
                    {'detail': 'You do not have permission to reschedule this appointment.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(appointment, data=request.data)
            serializer.is_valid(raise_exception=True)
            new_appointment = serializer.save()

            return Response(
                AppointmentSerializer(new_appointment).data,
                status=status.HTTP_201_CREATED
            )
        except Appointment.DoesNotExist:
            return Response(
                {'detail': 'Appointment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        """
        API endpoint for patients to get their own appointments.
        """
        user = request.user
        # import inspect

        # print("User Attributes and Values:")
        # attributes = inspect.getmembers(user)
        # user_attributes = [(name, value) for name, value in attributes if not inspect.ismethod(value) and not name.startswith('__')]
        # for name, value in user_attributes:
        #     print(f"{name}: {value}")
        if hasattr(user, 'patient'):
            print(f"User's Patient attribute: {user.patientprofile}")
        if user.role != 'PATIENT' or not hasattr(user, 'patientprofile'):

            return Response(
                {'detail': 'You must be a patient to access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Apply filters
        queryset = Appointment.objects.filter(patient=user.patientprofile)

        # Upcoming/past filter
        filter_type = request.query_params.get('filter', 'all')

        if filter_type == 'upcoming':
            queryset = queryset.filter(
                start_datetime__gte=timezone.now(),
                status__in=['SCHEDULED', 'CONFIRMED']
            )
        elif filter_type == 'past':
            queryset = queryset.filter(
                Q(start_datetime__lt=timezone.now()) |
                Q(status__in=['COMPLETED', 'CANCELLED', 'NO_SHOW', 'RESCHEDULED'])
            )

        queryset = queryset.order_by('start_datetime')
        serializer = AppointmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsDoctor])
    def doctor_schedule(self, request):
        """
        API endpoint for doctors to get their schedule.
        """
        user = request.user

        if user.role != 'DOCTOR' or not hasattr(user, 'doctorprofile'):
            return Response(
                {'detail': 'You must be a doctor to access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Apply filters
        queryset = Appointment.objects.filter(doctor=user.doctorprofile)

        # Date range
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(start_datetime__date__gte=start_date)
        else:
            # Default to today
            queryset = queryset.filter(start_datetime__date__gte=timezone.now().date())

        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(start_datetime__date__lte=end_date)

        # Status filter
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        else:
            # Default to active appointments
            queryset = queryset.filter(
                status__in=['SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS']
            )

        queryset = queryset.order_by('start_datetime')
        serializer = AppointmentSerializer(queryset, many=True)
        return Response(serializer.data)


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointment reminders.
    """
    queryset = AppointmentReminder.objects.all()
    serializer_class = AppointmentReminderSerializer

    def get_permissions(self):
        """
        - Admin can do anything
        - Doctors and patients have limited access
        """
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter reminders based on user role.
        """
        user = self.request.user

        # Admin/staff can see all
        if user.is_staff:
            return AppointmentReminder.objects.all()

        # Doctors can see reminders for their appointments
        if hasattr(user, 'doctorprofile'):
            return AppointmentReminder.objects.filter(appointment__doctor=user.doctorprofile)

        # Patients can see reminders for their appointments
        if hasattr(user, 'patientprofile'):
            return AppointmentReminder.objects.filter(appointment__patient=user.patientprofile)

        # Other users can't see any reminders
        return AppointmentReminder.objects.none()

    def perform_create(self, serializer):
        """
        Create a reminder and check user permissions.
        """
        appointment_id = serializer.validated_data.get('apppointment')
        print(f"The appointment id here is", appointment_id)
        appointment = get_object_or_404(Appointment, id=appointment_id)

        user = self.request.user

        # Only admin/staff, the doctor, or the patient can add reminders
        if not user.is_staff and not (
            (hasattr(user, 'doctorprofile') and appointment.doctor == user.doctorprofile) or
            (hasattr(user, 'patientprofile') and appointment.patient == user.patientprofile)
        ):
            self.permission_denied(
                self.request,
                message="You do not have permission to add reminders for this appointment."
            )

        serializer.save()

    def perform_update(self, serializer):
        """
        Update a reminder and check user permissions.
        """
        reminder = self.get_object()
        user = self.request.user

        # Only admin/staff, the doctor, or the patient can update reminders
        if not user.is_staff and not (
            (hasattr(user, 'doctor') and reminder.appointment.doctor == user.doctor) or
            (hasattr(user, 'patient') and reminder.appointment.patient == user.patient)
        ):
            self.permission_denied(
                self.request,
                message="You do not have permission to update this reminder."
            )

        # Don't allow updating sent reminders
        if reminder.sent:
            self.permission_denied(
                self.request,
                message="Cannot update a reminder that has already been sent."
            )

        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a reminder and check user permissions.
        """
        user = self.request.user

        # Only admin/staff, the doctor, or the patient can delete reminders
        if not user.is_staff and not (
            (hasattr(user, 'doctor') and instance.appointment.doctor == user.doctor) or
            (hasattr(user, 'patient') and instance.appointment.patient == user.patient)
        ):
            self.permission_denied(
                self.request,
                message="You do not have permission to delete this reminder."
            )

        # Don't allow deleting sent reminders
        if instance.sent:
            self.permission_denied(
                self.request,
                message="Cannot delete a reminder that has already been sent."
            )

        instance.delete()