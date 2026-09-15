
from django.conf import settings
from django.db import models


class Complaint(models.Model):

    class ComplaintType(models.TextChoices):
        ORDER = "ORDER", "Order Issue"
        PRODUCT = "PRODUCT", "Product Issue"
        SELLER = "SELLER", "Seller Issue"
        DELIVERY = "DELIVERY", "Delivery Issue"
        PAYMENT = "PAYMENT", "Payment Issue"
        RETURN = "RETURN", "Return Issue"
        REFUND = "REFUND", "Refund Issue"
        ACCOUNT = "ACCOUNT", "Account Issue"
        OTHER = "OTHER", "Other"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        WAITING_FOR_CUSTOMER = "WAITING_FOR_CUSTOMER", "Waiting for Customer"
        WAITING_FOR_SELLER = "WAITING_FOR_SELLER", "Waiting for Seller"
        RESOLVED = "RESOLVED", "Resolved"
        REJECTED = "REJECTED", "Rejected"
        CLOSED = "CLOSED", "Closed"

    complaint_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="complaints",
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="complaints",
        null=True,
        blank=True,
    )

    order_item = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.PROTECT,
        related_name="complaints",
        null=True,
        blank=True,
    )

    complaint_type = models.CharField(
        max_length=20,
        choices=ComplaintType.choices,
    )

    subject = models.CharField(max_length=200)

    description = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
    )

    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_complaints",
        null=True,
        blank=True,
    )

    assigned_seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="seller_complaints",
        null=True,
        blank=True,
    )

    admin_note = models.TextField(
        blank=True,
        default="",
    )

    seller_note = models.TextField(
        blank=True,
        default="",
    )

    resolution = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.complaint_number:
            last_complaint = (
                Complaint.objects
                .order_by("-id")
                .first()
            )

            if last_complaint:
                next_number = last_complaint.id + 1
            else:
                next_number = 1

            self.complaint_number = (
                f"CMP-{next_number:08d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.complaint_number} - "
            f"{self.subject} - "
            f"{self.status}"
        )


class ComplaintAttachment(models.Model):

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(
        upload_to="complaint_attachments/%Y/%m/"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="complaint_attachments",
    )

    note = models.CharField(
        max_length=300,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.complaint.complaint_number} - "
            f"{self.file.name}"
        )


class ComplaintMessage(models.Model):

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="complaint_messages",
    )

    message = models.TextField()

    is_internal = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.complaint.complaint_number} - "
            f"{self.sender.email}"
        )
