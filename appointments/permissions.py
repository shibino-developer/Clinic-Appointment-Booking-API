from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'DOCTOR'


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PATIENT'