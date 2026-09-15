from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "seller",
            "product_name",
            "product_price",
            "unit",
            "quantity",
            "total_price",
            "created_at",
        ]

        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "receiver_name",
            "receiver_phone",
            "state",
            "district",
            "village",
            "address",
            "pincode",
            "payment_method",
            "payment_status",
            "order_status",
            "subtotal",
            "delivery_charge",
            "total_amount",
            "note",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "order_number",
            "user",
            "payment_status",
            "order_status",
            "subtotal",
            "delivery_charge",
            "total_amount",
            "items",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    receiver_name = serializers.CharField(
        max_length=150,
    )

    receiver_phone = serializers.CharField(
        max_length=15,
    )

    state = serializers.CharField(
        max_length=100,
    )

    district = serializers.CharField(
        max_length=100,
    )

    village = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
    )

    address = serializers.CharField()

    pincode = serializers.CharField(
        max_length=10,
    )

    payment_method = serializers.ChoiceField(
        choices=[
            ("COD", "Cash on Delivery"),
        ],
        default="COD",
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_receiver_phone(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        return value

    def validate_pincode(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Pincode must contain only digits."
            )

        if len(value) != 6:
            raise serializers.ValidationError(
                "Pincode must be 6 digits."
            )

        return value