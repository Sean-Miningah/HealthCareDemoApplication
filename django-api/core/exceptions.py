from rest_framework.exceptions import APIException
from rest_framework import status

class AppointmentConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The requested appointment time conflicts with an existing appointment."
    default_code = "appointment_conflict"

class DoctorUnavailableError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The doctor is not available at the requested time."
    default_code = "doctor_unavailable"
    