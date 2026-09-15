from django.conf import settings
from django.db import models
from orders.models import Order


class Delivery(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ASSIGNED = "ASSIGNED", "Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="delivery",
    )

    delivery_partner_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    delivery_partner_phone = models.CharField(
        max_length=15,
        blank=True,
        default="",
    )

    tracking_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    estimated_delivery_date = models.DateField(
        null=True,
        blank=True,
    )

    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivery_note = models.TextField(
        blank=True,
        default="",
    )

    # Customer delivery confirmation
    customer_otp_verified = models.BooleanField(
        default=False,
    )

    customer_otp_verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class DeliveryProof(models.Model):
    class ProofType(models.TextChoices):
        PARCEL = "PARCEL", "Parcel Photo"
        LABEL = "LABEL", "Label Photo"
        EXPIRY = "EXPIRY", "Expiry/Batch Photo"
        HANDOVER = "HANDOVER", "Handover Photo"
        OTHER = "OTHER", "Other Photo"

    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name="proofs",
    )

    proof_type = models.CharField(
        max_length=20,
        choices=ProofType.choices,
    )

    image = models.ImageField(
        upload_to="delivery_proofs/%Y/%m/",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    captured_at = models.DateTimeField(
        auto_now_add=True,
    )

    note = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.delivery.order.order_number} - "
            f"{self.get_proof_type_display()}"
        )