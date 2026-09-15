from rest_framework import serializers

from .models import Delivery, DeliveryProof


class DeliveryProofSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="delivery.order.order_number",
        read_only=True,
    )

    class Meta:
        model = DeliveryProof

        fields = [
            "id",
            "delivery",
            "order_number",
            "proof_type",
            "image",
            "latitude",
            "longitude",
            "captured_at",
            "note",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "delivery",
            "order_number",
            "captured_at",
            "created_at",
        ]

    def validate_image(self, image):
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            raise serializers.ValidationError(
                "Image size must not exceed 5 MB."
            )

        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp",
        ]

        if image.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only JPG, PNG and WEBP images are allowed."
            )

        return image


class DeliverySerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    proofs = DeliveryProofSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Delivery

        fields = [
            "id",
            "order",
            "order_number",
            "delivery_partner_name",
            "delivery_partner_phone",
            "tracking_number",
            "status",
            "estimated_delivery_date",
            "picked_up_at",
            "delivered_at",
            "customer_otp_verified",
            "customer_otp_verified_at",
            "delivery_note",
            "proofs",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order_number",
            "picked_up_at",
            "delivered_at",
            "customer_otp_verified",
            "customer_otp_verified_at",
            "proofs",
            "created_at",
            "updated_at",
        ]

    def validate_delivery_partner_phone(self, value):
        value = value.strip()

        if value and not value.isdigit():
            raise serializers.ValidationError(
                "Delivery partner phone must contain only digits."
            )

        if value and len(value) != 10:
            raise serializers.ValidationError(
                "Delivery partner phone must be exactly 10 digits."
            )

        return value