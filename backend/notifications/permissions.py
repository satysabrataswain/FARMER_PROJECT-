from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):

    message = "Admin access required."

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
            and request.user.is_staff
        )