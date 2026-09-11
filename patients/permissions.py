from rest_framework.permissions import BasePermission


class IsPatientOwner(BasePermission):
    """
    Custom permission to ensure that only the user who created
    the patient record can view, update, or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
