from rest_framework.permissions import BasePermission


class IsFarmer(BasePermission):
    message = "Only Farmer/Buyer users can access this API."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "BUYER"


class IsSeller(BasePermission):
    message = "Only Seller users can access this API."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "SELLER"