from django.utils import timezone

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import Delivery, DeliveryProof
from .permissions import IsAdmin, IsSeller, IsBuyer
from .serializers import (
    DeliverySerializer,
    DeliveryProofSerializer,
)


class DeliveryCreateView(APIView):
    """
    Admin creates delivery for an order.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def post(self, request):
        order_id = request.data.get("order")

        if not order_id:
            return Response(
                {"detail": "Order ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(id=order_id)

        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if hasattr(order, "delivery"):
            return Response(
                {
                    "detail": (
                        "Delivery already exists "
                        "for this order."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.order_status == Order.OrderStatus.CANCELLED:
            return Response(
                {
                    "detail": (
                        "Cancelled order cannot be "
                        "assigned for delivery."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery = Delivery.objects.create(
            order=order,
            delivery_partner_name=request.data.get(
                "delivery_partner_name",
                "",
            ),
            delivery_partner_phone=request.data.get(
                "delivery_partner_phone",
                "",
            ),
            tracking_number=request.data.get(
                "tracking_number"
            ) or None,
            estimated_delivery_date=request.data.get(
                "estimated_delivery_date"
            ),
            delivery_note=request.data.get(
                "delivery_note",
                "",
            ),
            status=Delivery.Status.ASSIGNED,
        )

        serializer = DeliverySerializer(delivery)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class DeliveryListView(APIView):
    """
    Admin sees all deliveries.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get(self, request):
        deliveries = (
            Delivery.objects
            .select_related("order")
            .prefetch_related("proofs")
            .order_by("-created_at")
        )

        serializer = DeliverySerializer(
            deliveries,
            many=True,
        )

        return Response(serializer.data)


class BuyerDeliveryView(APIView):
    """
    Buyer sees delivery information
    of their own order.
    """

    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user,
            )

        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            delivery = order.delivery

        except Delivery.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Delivery has not been "
                        "created yet."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DeliverySerializer(delivery)

        return Response(serializer.data)


class SellerDeliveryListView(APIView):
    """
    Seller sees deliveries related
    to their products.
    """

    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    def get(self, request):
        deliveries = (
            Delivery.objects
            .select_related("order")
            .prefetch_related("proofs")
            .filter(
                order__items__seller=request.user
            )
            .distinct()
            .order_by("-created_at")
        )

        serializer = DeliverySerializer(
            deliveries,
            many=True,
        )

        return Response(serializer.data)


class DeliveryDetailView(APIView):
    """
    Admin can view/update delivery.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get_object(self, delivery_id):
        try:
            return (
                Delivery.objects
                .select_related("order")
                .prefetch_related("proofs")
                .get(id=delivery_id)
            )

        except Delivery.DoesNotExist:
            return None

    def get(self, request, delivery_id):
        delivery = self.get_object(delivery_id)

        if not delivery:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DeliverySerializer(delivery)

        return Response(serializer.data)

    def patch(self, request, delivery_id):
        delivery = self.get_object(delivery_id)

        if not delivery:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if delivery.status == Delivery.Status.DELIVERED:
            return Response(
                {
                    "detail": (
                        "Delivered delivery cannot "
                        "be edited."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DeliverySerializer(
            delivery,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)


class DeliveryProofUploadView(APIView):
    """
    Upload delivery proof photo.

    Photos can contain:
    - Parcel
    - Label
    - Expiry/Batch
    - Handover
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, delivery_id):

        try:
            delivery = Delivery.objects.get(
                id=delivery_id
            )

        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if delivery.status in [
            Delivery.Status.DELIVERED,
            Delivery.Status.CANCELLED,
        ]:
            return Response(
                {
                    "detail": (
                        "Proof cannot be uploaded "
                        "after delivery is closed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        proof_type = request.data.get("proof_type")

        allowed_types = [
            choice[0]
            for choice in DeliveryProof.ProofType.choices
        ]

        if proof_type not in allowed_types:
            return Response(
                {
                    "detail": "Invalid proof_type.",
                    "allowed_types": allowed_types,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = request.FILES.get("image")

        if not image:
            return Response(
                {"detail": "Proof image is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DeliveryProofSerializer(
            data={
                "proof_type": proof_type,
                "image": image,
                "latitude": request.data.get(
                    "latitude"
                ),
                "longitude": request.data.get(
                    "longitude"
                ),
                "note": request.data.get(
                    "note",
                    "",
                ),
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        proof = serializer.save(
            delivery=delivery
        )

        return Response(
            DeliveryProofSerializer(proof).data,
            status=status.HTTP_201_CREATED,
        )


class DeliveryStatusUpdateView(APIView):
    """
    Admin updates delivery status.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    allowed_transitions = {
        Delivery.Status.PENDING: [
            Delivery.Status.ASSIGNED,
            Delivery.Status.CANCELLED,
        ],

        Delivery.Status.ASSIGNED: [
            Delivery.Status.PICKED_UP,
            Delivery.Status.CANCELLED,
        ],

        Delivery.Status.PICKED_UP: [
            Delivery.Status.IN_TRANSIT,
            Delivery.Status.FAILED,
        ],

        Delivery.Status.IN_TRANSIT: [
            Delivery.Status.OUT_FOR_DELIVERY,
            Delivery.Status.FAILED,
        ],

        Delivery.Status.OUT_FOR_DELIVERY: [
            Delivery.Status.DELIVERED,
            Delivery.Status.FAILED,
        ],

        Delivery.Status.FAILED: [
            Delivery.Status.OUT_FOR_DELIVERY,
            Delivery.Status.CANCELLED,
        ],

        Delivery.Status.DELIVERED: [],

        Delivery.Status.CANCELLED: [],
    }

    def post(self, request, delivery_id):

        try:
            delivery = (
                Delivery.objects
                .select_related("order")
                .get(id=delivery_id)
            )

        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")

        valid_statuses = [
            choice[0]
            for choice in Delivery.Status.choices
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    "detail": "Invalid delivery status.",
                    "allowed_statuses": valid_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_next_statuses = (
            self.allowed_transitions.get(
                delivery.status,
                [],
            )
        )

        if new_status not in allowed_next_statuses:
            return Response(
                {
                    "detail": (
                        f"Cannot change delivery status "
                        f"from {delivery.status} "
                        f"to {new_status}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # DELIVERED se pehle proof required
        if new_status == Delivery.Status.DELIVERED:

            proof_count = delivery.proofs.count()

            if proof_count < 1:
                return Response(
                    {
                        "detail": (
                            "At least one delivery "
                            "proof photo is required "
                            "before marking delivered."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not delivery.customer_otp_verified:
                return Response(
                    {
                        "detail": (
                            "Customer OTP verification "
                            "is required before delivery."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        delivery.status = new_status

        now = timezone.now()

        if new_status == Delivery.Status.PICKED_UP:
            delivery.picked_up_at = now

        if new_status == Delivery.Status.DELIVERED:

            delivery.delivered_at = now

            order = delivery.order

            order.order_status = (
                Order.OrderStatus.DELIVERED
            )

            order.payment_status = (
                Order.PaymentStatus.PAID
            )

            order.save(
                update_fields=[
                    "order_status",
                    "payment_status",
                    "updated_at",
                ]
            )

        elif new_status == Delivery.Status.CANCELLED:

            delivery.order.order_status = (
                Order.OrderStatus.CANCELLED
            )

            delivery.order.save(
                update_fields=[
                    "order_status",
                    "updated_at",
                ]
            )

        elif new_status == Delivery.Status.OUT_FOR_DELIVERY:

            delivery.order.order_status = (
                Order.OrderStatus.OUT_FOR_DELIVERY
            )

            delivery.order.save(
                update_fields=[
                    "order_status",
                    "updated_at",
                ]
            )

        elif new_status == Delivery.Status.IN_TRANSIT:

            delivery.order.order_status = (
                Order.OrderStatus.SHIPPED
            )

            delivery.order.save(
                update_fields=[
                    "order_status",
                    "updated_at",
                ]
            )

        delivery.save()

        serializer = DeliverySerializer(delivery)

        return Response(serializer.data)


class CustomerDeliveryConfirmView(APIView):
    """
    Customer confirms delivery using OTP.

    NOTE:
    Actual OTP generation/SMS service will be connected
    later. For now this endpoint expects the OTP to be
    passed from the verified delivery flow.
    """

    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    def post(self, request, order_id):

        try:
            delivery = (
                Delivery.objects
                .select_related("order")
                .get(
                    order_id=order_id,
                    order__user=request.user,
                )
            )

        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if delivery.status != Delivery.Status.OUT_FOR_DELIVERY:
            return Response(
                {
                    "detail": (
                        "Delivery confirmation is "
                        "available only when the order "
                        "is out for delivery."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = request.data.get("otp")

        if not otp:
            return Response(
                {"detail": "OTP is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Temporary verification placeholder.
        # Real SMS OTP verification will be connected
        # with the notification/OTP service.
        expected_otp = request.data.get(
            "expected_otp"
        )

        if not expected_otp:
            return Response(
                {
                    "detail": (
                        "OTP service is not configured yet."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if str(otp) != str(expected_otp):
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery.customer_otp_verified = True
        delivery.customer_otp_verified_at = timezone.now()

        delivery.save(
            update_fields=[
                "customer_otp_verified",
                "customer_otp_verified_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Customer delivery "
                    "confirmed successfully."
                ),
                "customer_otp_verified": True,
            }
        )