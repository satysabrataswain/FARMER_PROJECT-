from rest_framework.permissions import BasePermission


class IsFarmer(BasePermission):
    message = "Only Farmer/Buyer users can access the Cart API."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "BUYER"