from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsDoctor(permissions.BasePermission):
    """
    Permission to only allow users with doctor role.
    """
    def has_permission(self, request, view):
        # Primary check should be on the user's role
        is_doctor_role = request.user.is_authenticated and request.user.role == 'DOCTOR'

        return is_doctor_role

class IsPatient(permissions.BasePermission):
    """
    Permission to only allow users with patient role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PATIENT'
