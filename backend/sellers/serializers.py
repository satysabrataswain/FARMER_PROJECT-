from rest_framework import serializers

from .models import SellerDocument, SellerProfile


class SellerProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    user_name = serializers.CharField(
        source="user.name",
        read_only=True,
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = SellerProfile

        fields = [
            "id",
            "user_id",
            "user_name",
            "user_email",
            "shop_name",
            "owner_name",
            "phone",
            "email",
            "state",
            "district",
            "village",
            "address",
            "pincode",
            "verification_status",
            "verification_note",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user_id",
            "user_name",
            "user_email",
            "verification_status",
            "verification_note",
            "created_at",
            "updated_at",
        ]

    def validate_shop_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Shop name is required."
            )

        return value

    def validate_owner_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Owner name is required."
            )

        return value

    def validate_phone(self, value):
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

    def validate_email(self, value):
        return value.lower().strip()

    def validate_state(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "State is required."
            )

        return value

    def validate_district(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "District is required."
            )

        return value

    def validate_village(self, value):
        return value.strip()

    def validate_address(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Address is required."
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
                "Pincode must contain exactly 6 digits."
            )

        return value


class SellerDocumentSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(
        source="seller.id",
        read_only=True,
    )

    seller_name = serializers.CharField(
        source="seller.shop_name",
        read_only=True,
    )

    document_type_display = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    verification_status_display = serializers.CharField(
        source="get_verification_status_display",
        read_only=True,
    )

    class Meta:
        model = SellerDocument

        fields = [
            "id",
            "seller_id",
            "seller_name",
            "document_type",
            "document_type_display",
            "document_number",
            "document_file",
            "issue_date",
            "expiry_date",
            "verification_status",
            "verification_status_display",
            "verification_note",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "seller_id",
            "seller_name",
            "document_type_display",
            "verification_status",
            "verification_status_display",
            "verification_note",
            "created_at",
            "updated_at",
        ]

    def validate_document_file(self, value):
        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Document file must be 5 MB or smaller."
            )

        allowed_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
        ]

        file_name = value.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise serializers.ValidationError(
                "Only PDF, JPG, JPEG and PNG files are allowed."
            )

        return value

    def validate(self, attrs):
        issue_date = attrs.get("issue_date")
        expiry_date = attrs.get("expiry_date")

        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                raise serializers.ValidationError({
                    "expiry_date": (
                        "Expiry date must be later "
                        "than issue date."
                    )
                })

        return attrs


class SellerDocumentVerificationSerializer(
    serializers.ModelSerializer
):
    """
    Admin serializer for document verification.
    """

    class Meta:
        model = SellerDocument

        fields = [
            "id",
            "verification_status",
            "verification_note",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_verification_status(self, value):
        allowed_statuses = [
            SellerDocument.VerificationStatus.APPROVED,
            SellerDocument.VerificationStatus.REJECTED,
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Status must be APPROVED or REJECTED."
            )

        return value

    def validate(self, attrs):
        status_value = attrs.get(
            "verification_status"
        )

        note = attrs.get(
            "verification_note",
            "",
        )

        if (
            status_value
            == SellerDocument.VerificationStatus.REJECTED
        ):
            if not note or not note.strip():
                raise serializers.ValidationError({
                    "verification_note": (
                        "Rejection reason is required."
                    )
                })

        return attrs


class SellerVerificationSerializer(
    serializers.ModelSerializer
):
    """
    Admin serializer for seller verification.
    """

    class Meta:
        model = SellerProfile

        fields = [
            "id",
            "verification_status",
            "verification_note",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_verification_status(self, value):
        allowed_statuses = [
            SellerProfile.VerificationStatus.APPROVED,
            SellerProfile.VerificationStatus.REJECTED,
            SellerProfile.VerificationStatus.SUSPENDED,
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Invalid verification status."
            )

        return value

    def validate(self, attrs):
        status_value = attrs.get(
            "verification_status"
        )

        note = attrs.get(
            "verification_note",
            "",
        )

        if (
            status_value
            == SellerProfile.VerificationStatus.REJECTED
        ):
            if not note or not note.strip():
                raise serializers.ValidationError({
                    "verification_note": (
                        "Rejection reason is required."
                    )
                })

        if (
            status_value
            == SellerProfile.VerificationStatus.SUSPENDED
        ):
            if not note or not note.strip():
                raise serializers.ValidationError({
                    "verification_note": (
                        "Suspension reason is required."
                    )
                })

        return attrs