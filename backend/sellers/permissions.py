from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    """
    Allows access only to SELLER users.
    """

    message = (
        "Only Seller users can access "
        "the Seller API."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "SELLER"


class IsAdmin(BasePermission):
    """
    Allows access only to ADMIN users.
    """

    message = (
        "Only Admin users can access "
        "the Seller Verification API."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.role == "ADMIN"
            and user.is_staff
        )