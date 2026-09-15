from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SellerDocument, SellerProfile
from .permissions import IsAdmin, IsSeller
from .serializers import (
    SellerDocumentSerializer,
    SellerDocumentVerificationSerializer,
    SellerProfileSerializer,
    SellerVerificationSerializer,
)


class SellerProfileView(APIView):
    """
    Seller Profile API.
    """

    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    def get_profile(self, user):
        try:
            return SellerProfile.objects.get(
                user=user
            )
        except SellerProfile.DoesNotExist:
            return None

    def get(self, request):
        profile = self.get_profile(
            request.user
        )

        if profile is None:
            return Response(
                {
                    "message": (
                        "Seller profile does not exist. "
                        "Please create your profile first."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerProfileSerializer(
            profile
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        profile = self.get_profile(
            request.user
        )

        if profile is not None:
            serializer = SellerProfileSerializer(
                profile,
                data=request.data,
                partial=False,
            )

            serializer.is_valid(
                raise_exception=True
            )

            serializer.save()

            return Response(
                {
                    "message": (
                        "Seller profile updated successfully."
                    ),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        serializer = SellerProfileSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = serializer.save(
            user=request.user
        )

        return Response(
            {
                "message": (
                    "Seller profile created successfully."
                ),
                "data": SellerProfileSerializer(
                    profile
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request):
        profile = self.get_profile(
            request.user
        )

        if profile is None:
            return Response(
                {
                    "message": (
                        "Seller profile does not exist. "
                        "Create the profile first."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Seller profile updated successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        profile = self.get_profile(
            request.user
        )

        if profile is None:
            return Response(
                {
                    "message": (
                        "Seller profile does not exist. "
                        "Create the profile first."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerProfileSerializer(
            profile,
            data=request.data,
            partial=False,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Seller profile updated successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SellerDocumentView(APIView):
    """
    Seller Document API.

    GET:
        List documents uploaded by logged-in seller.

    POST:
        Upload a new seller document.
    """

    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_profile(self, user):
        try:
            return SellerProfile.objects.get(
                user=user
            )
        except SellerProfile.DoesNotExist:
            return None

    def get(self, request):
        profile = self.get_profile(
            request.user
        )

        if profile is None:
            return Response(
                {
                    "message": (
                        "Seller profile does not exist."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        documents = SellerDocument.objects.filter(
            seller=profile
        ).order_by(
            "-created_at"
        )

        serializer = SellerDocumentSerializer(
            documents,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        profile = self.get_profile(
            request.user
        )

        if profile is None:
            return Response(
                {
                    "message": (
                        "Create Seller Profile "
                        "before uploading documents."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SellerDocumentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        document = serializer.save(
            seller=profile
        )

        return Response(
            {
                "message": (
                    "Seller document uploaded "
                    "successfully."
                ),
                "data": SellerDocumentSerializer(
                    document
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class SellerDocumentDetailView(APIView):
    """
    Seller can view or delete own document.
    """

    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    def get_profile(self, user):
        try:
            return SellerProfile.objects.get(
                user=user
            )
        except SellerProfile.DoesNotExist:
            return None

    def get_document(self, user, document_id):
        profile = self.get_profile(
            user
        )

        if profile is None:
            return None

        try:
            return SellerDocument.objects.get(
                id=document_id,
                seller=profile,
            )
        except SellerDocument.DoesNotExist:
            return None

    def get(self, request, document_id):
        document = self.get_document(
            request.user,
            document_id,
        )

        if document is None:
            return Response(
                {
                    "message": "Document not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerDocumentSerializer(
            document
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, document_id):
        document = self.get_document(
            request.user,
            document_id,
        )

        if document is None:
            return Response(
                {
                    "message": "Document not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            document.verification_status
            == SellerDocument.VerificationStatus.APPROVED
        ):
            return Response(
                {
                    "message": (
                        "Approved documents cannot "
                        "be deleted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document.delete()

        return Response(
            {
                "message": (
                    "Seller document deleted successfully."
                )
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class SellerVerificationListView(APIView):
    """
    Admin API.

    GET:
        List all sellers.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get(self, request):
        sellers = SellerProfile.objects.select_related(
            "user"
        ).prefetch_related(
            "documents"
        ).order_by(
            "-created_at"
        )

        serializer = SellerProfileSerializer(
            sellers,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class SellerVerificationDetailView(APIView):
    """
    Admin seller verification API.

    GET:
        View seller.

    PATCH:
        Approve, reject or suspend seller.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get_seller(self, seller_id):
        try:
            return SellerProfile.objects.select_related(
                "user"
            ).prefetch_related(
                "documents"
            ).get(
                id=seller_id
            )
        except SellerProfile.DoesNotExist:
            return None

    def get(self, request, seller_id):
        seller = self.get_seller(
            seller_id
        )

        if seller is None:
            return Response(
                {
                    "message": "Seller not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerProfileSerializer(
            seller
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, seller_id):
        seller = self.get_seller(
            seller_id
        )

        if seller is None:
            return Response(
                {
                    "message": "Seller not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerVerificationSerializer(
            seller,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Seller verification status "
                    "updated successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SellerDocumentVerificationDetailView(APIView):
    """
    Admin document verification API.

    GET:
        View one document.

    PATCH:
        Approve or reject document.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get_document(self, document_id):
        try:
            return SellerDocument.objects.select_related(
                "seller",
                "seller__user",
            ).get(
                id=document_id
            )
        except SellerDocument.DoesNotExist:
            return None

    def get(self, request, document_id):
        document = self.get_document(
            document_id
        )

        if document is None:
            return Response(
                {
                    "message": "Document not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerDocumentSerializer(
            document
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, document_id):
        document = self.get_document(
            document_id
        )

        if document is None:
            return Response(
                {
                    "message": "Document not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerDocumentVerificationSerializer(
            document,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Seller document verification "
                    "updated successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SellerDocumentListForAdminView(APIView):
    """
    Admin API to see all uploaded seller documents.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get(self, request):
        documents = SellerDocument.objects.select_related(
            "seller",
            "seller__user",
        ).order_by(
            "-created_at"
        )

        serializer = SellerDocumentSerializer(
            documents,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )