
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Public registration endpoint.

    Buyer and Seller can register.
    Admin cannot register through this API.
    """

    serializer_class = RegisterSerializer

    permission_classes = [
        AllowAny
    ]


class LoginView(TokenObtainPairView):
    """
    Login endpoint.

    Login uses:
        email + password

    Returns:
        access token
        refresh token
    """

    permission_classes = [
        AllowAny
    ]


class MeView(APIView):
    """
    Returns the currently authenticated user's information.
    """

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data
        )
