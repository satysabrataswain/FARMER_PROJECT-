from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    message = "Only Seller users can access this API."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "SELLER"


class IsAdmin(BasePermission):
    message = "Only Admin users can access this API."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "ADMIN" and user.is_staff