from django.conf import settings
from django.db import models


class SellerProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )

    shop_name = models.CharField(
        max_length=150,
        blank=False,
    )

    owner_name = models.CharField(
        max_length=150,
        blank=False,
    )

    phone = models.CharField(
        max_length=15,
        blank=False,
    )

    email = models.EmailField(
        blank=False,
    )

    state = models.CharField(
        max_length=100,
        blank=False,
    )

    district = models.CharField(
        max_length=100,
        blank=False,
    )

    village = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    address = models.TextField(
        blank=False,
    )

    pincode = models.CharField(
        max_length=10,
        blank=False,
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    verification_note = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.shop_name} - "
            f"{self.owner_name} - "
            f"{self.verification_status}"
        )


class SellerDocument(models.Model):
    class DocumentType(models.TextChoices):
        BUSINESS_REGISTRATION = (
            "BUSINESS_REGISTRATION",
            "Business Registration",
        )

        LICENSE = (
            "LICENSE",
            "License",
        )

        IDENTITY_PROOF = (
            "IDENTITY_PROOF",
            "Identity Proof",
        )

        ADDRESS_PROOF = (
            "ADDRESS_PROOF",
            "Address Proof",
        )

        TAX_DOCUMENT = (
            "TAX_DOCUMENT",
            "Tax Document",
        )

        OTHER = (
            "OTHER",
            "Other",
        )

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    seller = models.ForeignKey(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=40,
        choices=DocumentType.choices,
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    document_file = models.FileField(
        upload_to="seller_documents/%Y/%m/",
    )

    issue_date = models.DateField(
        null=True,
        blank=True,
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    verification_note = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.seller.shop_name} - "
            f"{self.get_document_type_display()} - "
            f"{self.verification_status}"
        )