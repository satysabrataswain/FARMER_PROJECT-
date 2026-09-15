
import os

from rest_framework import serializers

from .models import (
    Complaint,
    ComplaintAttachment,
    ComplaintMessage,
)


ALLOWED_FILE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
}


MAX_FILE_SIZE = 5 * 1024 * 1024


class ComplaintAttachmentSerializer(serializers.ModelSerializer):

    uploaded_by_name = serializers.CharField(
        source="uploaded_by.name",
        read_only=True,
    )

    class Meta:
        model = ComplaintAttachment
        fields = [
            "id",
            "complaint",
            "file",
            "uploaded_by",
            "uploaded_by_name",
            "note",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "complaint",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]

    def validate_file(self, value):

        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File size must not exceed 5 MB."
            )

        extension = os.path.splitext(
            value.name
        )[1].lower()

        if extension not in ALLOWED_FILE_EXTENSIONS:
            raise serializers.ValidationError(
                "Allowed files: JPG, JPEG, PNG, WEBP and PDF."
            )

        return value


class ComplaintMessageSerializer(serializers.ModelSerializer):

    sender_name = serializers.CharField(
        source="sender.name",
        read_only=True,
    )

    sender_role = serializers.CharField(
        source="sender.role",
        read_only=True,
    )

    class Meta:
        model = ComplaintMessage
        fields = [
            "id",
            "complaint",
            "sender",
            "sender_name",
            "sender_role",
            "message",
            "is_internal",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "complaint",
            "sender",
            "sender_name",
            "sender_role",
            "is_internal",
            "created_at",
        ]


class ComplaintSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    customer_email = serializers.CharField(
        source="customer.email",
        read_only=True,
    )

    assigned_admin_name = serializers.CharField(
        source="assigned_admin.name",
        read_only=True,
    )

    assigned_seller_name = serializers.CharField(
        source="assigned_seller.name",
        read_only=True,
    )

    attachments = ComplaintAttachmentSerializer(
        many=True,
        read_only=True,
    )

    messages = ComplaintMessageSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Complaint
        fields = [
            "id",
            "complaint_number",
            "customer",
            "customer_name",
            "customer_email",
            "order",
            "order_item",
            "complaint_type",
            "subject",
            "description",
            "priority",
            "status",
            "assigned_admin",
            "assigned_admin_name",
            "assigned_seller",
            "assigned_seller_name",
            "admin_note",
            "seller_note",
            "resolution",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
            "attachments",
            "messages",
        ]

        read_only_fields = [
            "id",
            "complaint_number",
            "customer",
            "customer_name",
            "customer_email",
            "assigned_admin",
            "assigned_admin_name",
            "assigned_seller",
            "assigned_seller_name",
            "status",
            "admin_note",
            "seller_note",
            "resolution",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
            "attachments",
            "messages",
        ]

    def validate(self, attrs):

        order = attrs.get("order")
        order_item = attrs.get("order_item")

        if order_item and order:
            if order_item.order_id != order.id:
                raise serializers.ValidationError(
                    "Order item does not belong to the selected order."
                )

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            if order and order.user_id != request.user.id:
                raise serializers.ValidationError(
                    "You can only create complaints for your own orders."
                )

            if order_item and order_item.order.user_id != request.user.id:
                raise serializers.ValidationError(
                    "You can only complain about your own order items."
                )

        return attrs


class ComplaintCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = [
            "order",
            "order_item",
            "complaint_type",
            "subject",
            "description",
            "priority",
        ]

    def validate(self, attrs):

        order = attrs.get("order")
        order_item = attrs.get("order_item")

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            if order and order.user_id != request.user.id:
                raise serializers.ValidationError(
                    "You can only create complaints for your own orders."
                )

            if order_item:

                if order_item.order.user_id != request.user.id:
                    raise serializers.ValidationError(
                        "You can only complain about your own order item."
                    )

                if order and order_item.order_id != order.id:
                    raise serializers.ValidationError(
                        "Order item does not belong to the selected order."
                    )

        return attrs


class ComplaintMessageCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = ComplaintMessage
        fields = [
            "message",
        ]

    def validate_message(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        if len(value) > 5000:
            raise serializers.ValidationError(
                "Message cannot exceed 5000 characters."
            )

        return value


class ComplaintStatusSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=Complaint.Status.choices
    )

    admin_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    seller_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    resolution = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    assigned_admin = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    assigned_seller = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):

        status = attrs.get("status")

        if status == Complaint.Status.RESOLVED:

            resolution = attrs.get(
                "resolution",
                ""
            ).strip()

            if not resolution:
                raise serializers.ValidationError(
                    {
                        "resolution":
                        "Resolution is required when resolving a complaint."
                    }
                )

        return attrs
