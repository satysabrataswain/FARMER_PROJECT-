
from django.conf import settings
from django.db import models


class FarmerProfile(models.Model):
    """
    Profile information for a Buyer/Farmer.

    One User can have one FarmerProfile.
    """

    class Language(models.TextChoices):
        HINDI = "HINDI", "Hindi"
        ENGLISH = "ENGLISH", "English"
        ODIA = "ODIA", "Odia"
        BENGALI = "BENGALI", "Bengali"
        TELUGU = "TELUGU", "Telugu"
        OTHER = "OTHER", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
    )

    village = models.CharField(
        max_length=150,
        blank=True,
    )

    language = models.CharField(
        max_length=20,
        choices=Language.choices,
        default=Language.HINDI,
    )

    crops = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.name} - Farmer Profile"
