from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        ORDER_PLACED = "ORDER_PLACED", "Order Placed"
        ORDER_CONFIRMED = "ORDER_CONFIRMED", "Order Confirmed"
        ORDER_PROCESSING = "ORDER_PROCESSING", "Order Processing"
        ORDER_SHIPPED = "ORDER_SHIPPED", "Order Shipped"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        ORDER_DELIVERED = "ORDER_DELIVERED", "Order Delivered"
        ORDER_CANCELLED = "ORDER_CANCELLED", "Order Cancelled"

        RETURN_REQUESTED = "RETURN_REQUESTED", "Return Requested"
        RETURN_APPROVED = "RETURN_APPROVED", "Return Approved"
        RETURN_REJECTED = "RETURN_REJECTED", "Return Rejected"
        RETURN_PICKED_UP = "RETURN_PICKED_UP", "Return Picked Up"
        RETURN_RECEIVED = "RETURN_RECEIVED", "Return Received"

        REFUND_APPROVED = "REFUND_APPROVED", "Refund Approved"
        REFUND_PROCESSING = "REFUND_PROCESSING", "Refund Processing"
        REFUND_COMPLETED = "REFUND_COMPLETED", "Refund Completed"
        REFUND_FAILED = "REFUND_FAILED", "Refund Failed"

        SELLER_REGISTERED = "SELLER_REGISTERED", "Seller Registered"
        SELLER_APPROVED = "SELLER_APPROVED", "Seller Approved"
        SELLER_REJECTED = "SELLER_REJECTED", "Seller Rejected"

        NEW_ORDER_SELLER = "NEW_ORDER_SELLER", "New Order for Seller"

        SUSPICIOUS_RETURN = "SUSPICIOUS_RETURN", "Suspicious Return"

        SYSTEM = "SYSTEM", "System Notification"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=40,
        choices=NotificationType.choices,
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )

    is_read = models.BooleanField(
        default=False,
    )

    # Optional reference to related object.
    # Example:
    # Order ID / Return ID / Seller ID
    reference_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    reference_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["recipient", "is_read"]
            ),
            models.Index(
                fields=["recipient", "created_at"]
            ),
            models.Index(
                fields=["notification_type"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.recipient.email} - "
            f"{self.title}"
        )