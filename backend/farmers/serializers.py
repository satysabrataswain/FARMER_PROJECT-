
from rest_framework import serializers

from .models import FarmerProfile


class FarmerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating Farmer Profile.
    """

    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = FarmerProfile

        fields = [
            "id",
            "user",
            "state",
            "district",
            "village",
            "language",
            "crops",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]

    def validate_crops(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Crops must be provided as a list."
            )

        cleaned_crops = []

        for crop in value:
            if not isinstance(crop, str):
                raise serializers.ValidationError(
                    "Each crop must be a text value."
                )

            crop = crop.strip()

            if crop:
                cleaned_crops.append(crop)

        return cleaned_crops
