from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    class Category(models.TextChoices):
        SEEDS = "SEEDS", "Seeds"
        CROP_PROTECTION = (
            "CROP_PROTECTION",
            "Crop Protection Products",
        )
        SMALL_IRRIGATION = (
            "SMALL_IRRIGATION",
            "Small Irrigation Products",
        )

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending Verification"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        INACTIVE = "INACTIVE", "Inactive"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
    )

    name = models.CharField(max_length=200)

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
    )

    subcategory = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    brand = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    unit = models.CharField(
        max_length=50,
    )

    stock_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    sku = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    suitable_crops = models.JSONField(
        default=list,
        blank=True,
    )

    target_pest_disease = models.TextField(
        blank=True,
        default="",
    )

    usage_application = models.TextField(
        blank=True,
        default="",
    )

    manufacturer_details = models.TextField(
        blank=True,
        default="",
    )

    license_product_number = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    verified_label = models.FileField(
        upload_to="product_labels/%Y/%m/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
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
        return f"{self.name} - {self.seller.email}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="product_images/%Y/%m/",
    )

    display_order = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.product.name} - Image {self.display_order}"


class ProductVideo(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="video",
    )

    video = models.FileField(
        upload_to="product_videos/%Y/%m/",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.product.name} - Video"