from rest_framework.permissions import BasePermission


class IsAdminOrIsSelf(BasePermission):
    """
    Object-level permission to only allow superuser or user is same object
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user == obj:
            return True

        return False
