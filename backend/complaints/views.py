
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Complaint,
    ComplaintAttachment,
    ComplaintMessage,
)
from .permissions import (
    IsAdminUserRole,
    IsBuyer,
    IsSeller,
)
from .serializers import (
    ComplaintAttachmentSerializer,
    ComplaintCreateSerializer,
    ComplaintMessageCreateSerializer,
    ComplaintMessageSerializer,
    ComplaintSerializer,
    ComplaintStatusSerializer,
)


# ============================================================
# CUSTOMER / BUYER
# ============================================================

class CustomerComplaintListCreateView(
    generics.ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    def get_queryset(self):

        return (
            Complaint.objects
            .filter(customer=self.request.user)
            .select_related(
                "customer",
                "order",
                "order_item",
                "assigned_admin",
                "assigned_seller",
            )
            .prefetch_related(
                "attachments",
                "messages",
            )
        )

    def get_serializer_class(self):

        if self.request.method == "POST":
            return ComplaintCreateSerializer

        return ComplaintSerializer

    def perform_create(self, serializer):

        serializer.save(
            customer=self.request.user
        )


class CustomerComplaintDetailView(
    generics.RetrieveAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    serializer_class = ComplaintSerializer

    lookup_url_kwarg = "complaint_id"

    def get_queryset(self):

        return (
            Complaint.objects
            .filter(customer=self.request.user)
            .select_related(
                "customer",
                "order",
                "order_item",
                "assigned_admin",
                "assigned_seller",
            )
            .prefetch_related(
                "attachments",
                "messages",
            )
        )


class CustomerComplaintMessageView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    serializer_class = ComplaintMessageCreateSerializer

    def get_complaint(self):

        return Complaint.objects.filter(
            id=self.kwargs["complaint_id"],
            customer=self.request.user,
        ).first()

    def create(self, request, *args, **kwargs):

        complaint = self.get_complaint()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if complaint.status in [
            Complaint.Status.CLOSED,
            Complaint.Status.REJECTED,
        ]:
            return Response(
                {
                    "detail":
                    "This complaint is closed and cannot receive new messages."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        message = ComplaintMessage.objects.create(
            complaint=complaint,
            sender=request.user,
            message=serializer.validated_data["message"],
            is_internal=False,
        )

        complaint.status = (
            Complaint.Status.UNDER_REVIEW
        )

        complaint.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            ComplaintMessageSerializer(
                message
            ).data,
            status=status.HTTP_201_CREATED,
        )


class CustomerComplaintAttachmentView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    serializer_class = ComplaintAttachmentSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def create(self, request, *args, **kwargs):

        complaint = Complaint.objects.filter(
            id=self.kwargs["complaint_id"],
            customer=request.user,
        ).first()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if complaint.status in [
            Complaint.Status.CLOSED,
            Complaint.Status.REJECTED,
        ]:
            return Response(
                {
                    "detail":
                    "This complaint is closed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        attachment = serializer.save(
            complaint=complaint,
            uploaded_by=request.user,
        )

        return Response(
            ComplaintAttachmentSerializer(
                attachment
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# SELLER
# ============================================================

class SellerComplaintListView(
    generics.ListAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    serializer_class = ComplaintSerializer

    def get_queryset(self):

        return (
            Complaint.objects
            .filter(
                assigned_seller=self.request.user
            )
            .select_related(
                "customer",
                "order",
                "order_item",
                "assigned_admin",
                "assigned_seller",
            )
            .prefetch_related(
                "attachments",
                "messages",
            )
        )


class SellerComplaintMessageView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    serializer_class = ComplaintMessageCreateSerializer

    def create(self, request, *args, **kwargs):

        complaint = Complaint.objects.filter(
            id=self.kwargs["complaint_id"],
            assigned_seller=request.user,
        ).first()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if complaint.status in [
            Complaint.Status.CLOSED,
            Complaint.Status.REJECTED,
        ]:
            return Response(
                {
                    "detail":
                    "This complaint is closed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        message = ComplaintMessage.objects.create(
            complaint=complaint,
            sender=request.user,
            message=serializer.validated_data["message"],
            is_internal=False,
        )

        complaint.status = (
            Complaint.Status.IN_PROGRESS
        )

        complaint.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            ComplaintMessageSerializer(
                message
            ).data,
            status=status.HTTP_201_CREATED,
        )


class SellerComplaintAttachmentView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    serializer_class = ComplaintAttachmentSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def create(self, request, *args, **kwargs):

        complaint = Complaint.objects.filter(
            id=self.kwargs["complaint_id"],
            assigned_seller=request.user,
        ).first()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        attachment = serializer.save(
            complaint=complaint,
            uploaded_by=request.user,
        )

        return Response(
            ComplaintAttachmentSerializer(
                attachment
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# ADMIN
# ============================================================

class AdminComplaintListView(
    generics.ListAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdminUserRole,
    ]

    serializer_class = ComplaintSerializer

    def get_queryset(self):

        queryset = (
            Complaint.objects
            .all()
            .select_related(
                "customer",
                "order",
                "order_item",
                "assigned_admin",
                "assigned_seller",
            )
            .prefetch_related(
                "attachments",
                "messages",
            )
        )

        complaint_status = self.request.query_params.get(
            "status"
        )

        priority = self.request.query_params.get(
            "priority"
        )

        complaint_type = self.request.query_params.get(
            "type"
        )

        if complaint_status:
            queryset = queryset.filter(
                status=complaint_status
            )

        if priority:
            queryset = queryset.filter(
                priority=priority
            )

        if complaint_type:
            queryset = queryset.filter(
                complaint_type=complaint_type
            )

        return queryset


class AdminComplaintDetailView(
    generics.RetrieveAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdminUserRole,
    ]

    serializer_class = ComplaintSerializer

    lookup_url_kwarg = "complaint_id"

    queryset = (
        Complaint.objects
        .all()
        .select_related(
            "customer",
            "order",
            "order_item",
            "assigned_admin",
            "assigned_seller",
        )
        .prefetch_related(
            "attachments",
            "messages",
        )
    )


class AdminComplaintStatusView(
    generics.UpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdminUserRole,
    ]

    serializer_class = ComplaintStatusSerializer

    http_method_names = [
        "patch",
    ]

    def get_object(self):

        return Complaint.objects.get(
            id=self.kwargs["complaint_id"]
        )

    def patch(self, request, *args, **kwargs):

        complaint = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        if "status" in data:
            complaint.status = data["status"]

        if "admin_note" in data:
            complaint.admin_note = data[
                "admin_note"
            ]

        if "seller_note" in data:
            complaint.seller_note = data[
                "seller_note"
            ]

        if "resolution" in data:
            complaint.resolution = data[
                "resolution"
            ]

        if "assigned_admin" in data:

            admin_id = data[
                "assigned_admin"
            ]

            if admin_id is None:
                complaint.assigned_admin = None

            else:
                from django.contrib.auth import get_user_model

                User = get_user_model()

                admin = User.objects.filter(
                    id=admin_id,
                    role="ADMIN",
                    is_staff=True,
                ).first()

                if not admin:
                    return Response(
                        {
                            "detail":
                            "Invalid admin user."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                complaint.assigned_admin = admin

        if "assigned_seller" in data:

            seller_id = data[
                "assigned_seller"
            ]

            if seller_id is None:
                complaint.assigned_seller = None

            else:
                from django.contrib.auth import get_user_model

                User = get_user_model()

                seller = User.objects.filter(
                    id=seller_id,
                    role="SELLER",
                    is_active=True,
                ).first()

                if not seller:
                    return Response(
                        {
                            "detail":
                            "Invalid seller user."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                complaint.assigned_seller = seller

        if complaint.status == Complaint.Status.RESOLVED:

            complaint.resolved_at = timezone.now()

        if complaint.status == Complaint.Status.CLOSED:

            complaint.closed_at = timezone.now()

        complaint.save()

        return Response(
            ComplaintSerializer(
                complaint
            ).data
        )


class AdminComplaintMessageView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdminUserRole,
    ]

    serializer_class = ComplaintMessageCreateSerializer

    def create(self, request, *args, **kwargs):

        complaint = Complaint.objects.filter(
            id=self.kwargs["complaint_id"]
        ).first()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        message = ComplaintMessage.objects.create(
            complaint=complaint,
            sender=request.user,
            message=serializer.validated_data["message"],
            is_internal=False,
        )

        if complaint.status == Complaint.Status.OPEN:
            complaint.status = (
                Complaint.Status.UNDER_REVIEW
            )
            complaint.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            ComplaintMessageSerializer(
                message
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminInternalComplaintMessageView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdminUserRole,
    ]

    serializer_class = ComplaintMessageCreateSerializer

    def create(self, request, *args, **kwargs):

        complaint = Complaint.objects.filter(
            id=self.kwargs["complaint_id"]
        ).first()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        message = ComplaintMessage.objects.create(
            complaint=complaint,
            sender=request.user,
            message=serializer.validated_data["message"],
            is_internal=True,
        )

        return Response(
            ComplaintMessageSerializer(
                message
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminComplaintAttachmentView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdminUserRole,
    ]

    serializer_class = ComplaintAttachmentSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def create(self, request, *args, **kwargs):

        complaint = Complaint.objects.filter(
            id=self.kwargs["complaint_id"]
        ).first()

        if not complaint:
            return Response(
                {
                    "detail":
                    "Complaint not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        attachment = serializer.save(
            complaint=complaint,
            uploaded_by=request.user,
        )

        return Response(
            ComplaintAttachmentSerializer(
                attachment
            ).data,
            status=status.HTTP_201_CREATED,
        )