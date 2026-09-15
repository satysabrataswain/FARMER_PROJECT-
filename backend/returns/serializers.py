import re

from django.utils import timezone
from rest_framework import serializers

from orders.models import Order, OrderItem
from .models import ReturnRequest, ReturnProof


UPI_REGEX = r"^[A-Za-z0-9._-]{2,}@[A-Za-z0-9.-]{2,}$"


class ReturnProofSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReturnProof
        fields = [
            "id",
            "return_request",
            "proof_type",
            "image",
            "latitude",
            "longitude",
            "note",
            "captured_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "return_request",
            "captured_at",
            "created_at",
        ]


class ReturnRequestSerializer(serializers.ModelSerializer):

    proofs = ReturnProofSerializer(
        many=True,
        read_only=True,
    )

    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="order_item.product_name",
        read_only=True,
    )

    class Meta:
        model = ReturnRequest

        fields = [
            "id",
            "order",
            "order_number",
            "order_item",
            "product_name",
            "customer",
            "reason",
            "description",
            "status",

            "suspicious",
            "risk_score",
            "risk_level",
            "suspicious_reasons",
            "suspicious_reviewed",

            "return_batch_number",
            "return_expiry_date",

            "refund_status",
            "refund_amount",
            "refund_upi_id",
            "refund_transaction_id",
            "refund_processed_at",
            "refund_note",

            "admin_note",
            "seller_note",
            "pickup_address",
            "pickup_pincode",

            "requested_at",
            "approved_at",
            "picked_up_at",
            "received_at",
            "completed_at",
            "created_at",
            "updated_at",

            "proofs",
        ]

        read_only_fields = [
            "id",
            "customer",
            "status",

            "suspicious",
            "risk_score",
            "risk_level",
            "suspicious_reasons",
            "suspicious_reviewed",

            "refund_status",
            "refund_amount",
            "refund_transaction_id",
            "refund_processed_at",

            "approved_at",
            "picked_up_at",
            "received_at",
            "completed_at",

            "requested_at",
            "created_at",
            "updated_at",
        ]

    def validate_refund_upi_id(self, value):
        value = value.strip()

        if not value:
            return value

        if not re.match(UPI_REGEX, value):
            raise serializers.ValidationError(
                "Enter a valid UPI ID, for example farmer@upi."
            )

        return value

    def validate_order_item(self, order_item):

        request = self.context["request"]

        if order_item.order.user_id != request.user.id:
            raise serializers.ValidationError(
                "You can only return your own order item."
            )

        if order_item.order.order_status != Order.OrderStatus.DELIVERED:
            raise serializers.ValidationError(
                "Return can only be requested after delivery."
            )

        existing = ReturnRequest.objects.filter(
            order_item=order_item
        ).exclude(
            status__in=[
                ReturnRequest.Status.REJECTED,
                ReturnRequest.Status.CANCELLED,
            ]
        )

        if self.instance:
            existing = existing.exclude(
                id=self.instance.id
            )

        if existing.exists():
            raise serializers.ValidationError(
                "A return request already exists for this order item."
            )

        return order_item

    def create(self, validated_data):

        request = self.context["request"]

        return_request = ReturnRequest.objects.create(
            customer=request.user,
            status=ReturnRequest.Status.UNDER_REVIEW,
            **validated_data,
        )

        return_request.refund_amount = (
            return_request.calculate_refund_amount()
        )

        return_request.save()

        return return_request


class CustomerUPIRefundSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReturnRequest

        fields = [
            "refund_upi_id",
        ]

    def validate_refund_upi_id(self, value):

        value = value.strip()

        if not re.match(UPI_REGEX, value):
            raise serializers.ValidationError(
                "Enter a valid UPI ID, for example farmer@upi."
            )

        return value

    def validate(self, attrs):

        return_request = self.instance

        if return_request.status not in [
            ReturnRequest.Status.APPROVED,
            ReturnRequest.Status.PICKUP_ASSIGNED,
            ReturnRequest.Status.PICKED_UP,
            ReturnRequest.Status.RECEIVED,
        ]:
            raise serializers.ValidationError(
                "UPI ID can be submitted only after return approval."
            )

        if return_request.refund_status in [
            ReturnRequest.RefundStatus.COMPLETED,
            ReturnRequest.RefundStatus.PROCESSING,
        ]:
            raise serializers.ValidationError(
                "Refund is already being processed or completed."
            )

        return attrs


class ReturnReviewSerializer(serializers.Serializer):

    action = serializers.ChoiceField(
        choices=[
            "APPROVE",
            "REJECT",
            "SUSPICIOUS",
        ]
    )

    admin_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    suspicious_reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ReturnStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=[
            ReturnRequest.Status.PICKUP_ASSIGNED,
            ReturnRequest.Status.PICKED_UP,
            ReturnRequest.Status.RECEIVED,
            ReturnRequest.Status.COMPLETED,
            ReturnRequest.Status.CANCELLED,
        ]
    )

    admin_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RefundStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=[
            ReturnRequest.RefundStatus.APPROVED,
            ReturnRequest.RefundStatus.PROCESSING,
            ReturnRequest.RefundStatus.COMPLETED,
            ReturnRequest.RefundStatus.FAILED,
            ReturnRequest.RefundStatus.REJECTED,
        ]
    )

    transaction_id = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    refund_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )