from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles Buyer and Seller registration.

    Admin registration is not allowed through public API.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "name",
            "email",
            "phone",
            "password",
            "password2",
            "role",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Name is required."
            )

        return value

    def validate_email(self, value):
        return value.lower().strip()

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

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Admin registration is not allowed."
            )

        if value not in [
            User.Role.BUYER,
            User.Role.SELLER,
        ]:
            raise serializers.ValidationError(
                "Invalid user role."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Returns safe authenticated user information.

    Password is never returned.
    """

    class Meta:
        model = User

        fields = [
            "id",
            "name",
            "email",
            "phone",
            "role",
            "is_verified",
            "created_at",
        ]

        read_only_fields = fields