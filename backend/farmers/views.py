
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import FarmerProfile
from .serializers import FarmerProfileSerializer


class FarmerProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the logged-in farmer's profile.

    GET:
        Returns farmer profile.

    PUT/PATCH:
        Updates farmer profile.
    """

    serializer_class = FarmerProfileSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(self):
        profile, created = FarmerProfile.objects.get_or_create(
            user=self.request.user
        )

        return profile

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()

        serializer = self.get_serializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        profile = self.get_object()

        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
