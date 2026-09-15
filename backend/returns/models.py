from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from orders.models import Order, OrderItem


class ReturnRequest(models.Model):

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        PICKUP_ASSIGNED = "PICKUP_ASSIGNED", "Pickup Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        RECEIVED = "RECEIVED", "Received"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        SUSPICIOUS = "SUSPICIOUS", "Suspicious"

    class Reason(models.TextChoices):
        DAMAGED = "DAMAGED", "Damaged Product"
        WRONG_PRODUCT = "WRONG_PRODUCT", "Wrong Product"
        EXPIRED = "EXPIRED", "Expired Product"
        MISSING = "MISSING", "Missing Product"
        NOT_AS_DESCRIBED = "NOT_AS_DESCRIBED", "Product Not As Described"
        QUALITY_ISSUE = "QUALITY_ISSUE", "Quality Issue"
        OTHER = "OTHER", "Other"

    class RefundStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        REJECTED = "REJECTED", "Rejected"

    class RiskLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="return_requests",
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.PROTECT,
        related_name="return_requests",
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="return_requests",
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.REQUESTED,
    )

    # -------------------------
    # Suspicious Return System
    # -------------------------

    suspicious = models.BooleanField(
        default=False,
    )

    risk_score = models.PositiveSmallIntegerField(
        default=0,
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )

    suspicious_reasons = models.JSONField(
        default=list,
        blank=True,
    )

    suspicious_reviewed = models.BooleanField(
        default=False,
    )

    # Customer-entered product information
    return_batch_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    return_expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    # -------------------------
    # Refund System
    # -------------------------

    refund_status = models.CharField(
        max_length=30,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
    )

    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    refund_upi_id = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    refund_transaction_id = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    refund_processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    refund_note = models.TextField(
        blank=True,
        default="",
    )

    # -------------------------
    # Notes
    # -------------------------

    admin_note = models.TextField(
        blank=True,
        default="",
    )

    seller_note = models.TextField(
        blank=True,
        default="",
    )

    pickup_address = models.TextField(
        blank=True,
        default="",
    )

    pickup_pincode = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )

    # -------------------------
    # Dates
    # -------------------------

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    received_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def calculate_refund_amount(self):
        """
        COD refund amount.

        Initial policy:
        product price × returned quantity

        Delivery charge is not included.
        """

        amount = (
            self.order_item.product_price
            * self.order_item.quantity
        )

        return Decimal(amount).quantize(
            Decimal("0.01")
        )

    def save(self, *args, **kwargs):

        if self.order_item_id:
            self.refund_amount = self.calculate_refund_amount()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.order.order_number} - "
            f"{self.order_item.product_name} - "
            f"{self.status}"
        )


class ReturnProof(models.Model):

    class ProofType(models.TextChoices):
        CUSTOMER_PRODUCT = (
            "CUSTOMER_PRODUCT",
            "Customer Product Photo",
        )

        CUSTOMER_LABEL = (
            "CUSTOMER_LABEL",
            "Customer Label Photo",
        )

        CUSTOMER_EXPIRY = (
            "CUSTOMER_EXPIRY",
            "Customer Expiry/Batch Photo",
        )

        PICKUP = (
            "PICKUP",
            "Pickup Photo",
        )

        RECEIVED = (
            "RECEIVED",
            "Received Product Photo",
        )

        RECEIVED_LABEL = (
            "RECEIVED_LABEL",
            "Received Label Photo",
        )

        RECEIVED_EXPIRY = (
            "RECEIVED_EXPIRY",
            "Received Expiry/Batch Photo",
        )

        OTHER = (
            "OTHER",
            "Other Photo",
        )

    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name="proofs",
    )

    proof_type = models.CharField(
        max_length=30,
        choices=ProofType.choices,
    )

    image = models.ImageField(
        upload_to="return_proofs/%Y/%m/",
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

    note = models.TextField(
        blank=True,
        default="",
    )

    captured_at = models.DateTimeField(
        auto_now_add=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.return_request.id} - "
            f"{self.get_proof_type_display()}"
        )