
from django.contrib import admin

from .models import FarmerProfile


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "state",
        "district",
        "village",
        "language",
        "created_at",
    )

    list_filter = (
        "language",
        "state",
        "district",
    )

    search_fields = (
        "user__name",
        "user__email",
        "user__phone",
        "state",
        "district",
        "village",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
