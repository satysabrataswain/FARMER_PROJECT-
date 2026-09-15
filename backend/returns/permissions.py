from rest_framework.permissions import BasePermission


class IsBuyer(BasePermission):

    message = "Only buyers can perform this action."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "BUYER"
        )


class IsSeller(BasePermission):

    message = "Only sellers can perform this action."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "SELLER"
        )


class IsAdmin(BasePermission):

    message = "Only admin can perform this action."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
            and request.user.is_staff
        )