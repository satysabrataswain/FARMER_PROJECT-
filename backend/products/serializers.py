from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Product, ProductImage, ProductVideo


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "display_order",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = [
            "id",
            "video",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )

    video = ProductVideoSerializer(
        read_only=True,
    )

    seller_name = serializers.CharField(
        source="seller.name",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "seller",
            "seller_name",
            "name",
            "category",
            "subcategory",
            "brand",
            "description",
            "price",
            "unit",
            "stock_quantity",
            "sku",
            "suitable_crops",
            "target_pest_disease",
            "usage_application",
            "manufacturer_details",
            "license_product_number",
            "verified_label",
            "status",
            "verification_note",
            "images",
            "video",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "seller",
            "seller_name",
            "status",
            "verification_note",
            "created_at",
            "updated_at",
        ]

    def validate_suitable_crops(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "suitable_crops must be a list."
            )

        return value

    def validate(self, attrs):
        category = attrs.get(
            "category",
            getattr(self.instance, "category", None),
        )

        if category == Product.Category.CROP_PROTECTION:
            if not attrs.get(
                "target_pest_disease",
                getattr(
                    self.instance,
                    "target_pest_disease",
                    "",
                ),
            ):
                raise serializers.ValidationError({
                    "target_pest_disease": (
                        "This field is required for Crop "
                        "Protection Products."
                    )
                })

        return attrs


class ProductCreateSerializer(ProductSerializer):
    pass


class ProductVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "status",
            "verification_note",
        ]

    def validate_status(self, value):
        allowed = [
            Product.Status.APPROVED,
            Product.Status.REJECTED,
            Product.Status.INACTIVE,
        ]

        if value not in allowed:
            raise serializers.ValidationError(
                "Invalid product verification status."
            )

        return value

    def validate(self, attrs):
        status = attrs.get("status")

        if status in [
            Product.Status.REJECTED,
            Product.Status.INACTIVE,
        ]:
            note = attrs.get(
                "verification_note",
                "",
            ).strip()

            if not note:
                raise serializers.ValidationError({
                    "verification_note": (
                        "Verification note is required."
                    )
                })

        return attrs


class ProductImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "display_order",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_image(self, value):
        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Image size must not exceed 5 MB."
            )

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]

        extension = value.name.lower().rsplit(".", 1)

        if len(extension) != 2:
            raise serializers.ValidationError(
                "Invalid image file."
            )

        extension = "." + extension[-1]

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        return value


class ProductVideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = [
            "id",
            "video",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_video(self, value):
        max_size = 50 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Video size must not exceed 50 MB."
            )

        allowed_extensions = [
            ".mp4",
            ".mov",
            ".webm",
        ]

        extension = value.name.lower().rsplit(".", 1)

        if len(extension) != 2:
            raise serializers.ValidationError(
                "Invalid video file."
            )

        extension = "." + extension[-1]

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only MP4, MOV and WEBM videos are allowed."
            )

        return value