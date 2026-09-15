from django.contrib import admin

from .models import SellerDocument, SellerProfile


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "shop_name",
        "owner_name",
        "phone",
        "state",
        "district",
        "verification_status",
        "created_at",
    )

    list_filter = (
        "verification_status",
        "state",
        "district",
    )

    search_fields = (
        "shop_name",
        "owner_name",
        "phone",
        "email",
        "user__email",
        "user__name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25


@admin.register(SellerDocument)
class SellerDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "seller",
        "document_type",
        "document_number",
        "issue_date",
        "expiry_date",
        "verification_status",
        "created_at",
    )

    list_filter = (
        "document_type",
        "verification_status",
        "issue_date",
        "expiry_date",
    )

    search_fields = (
        "seller__shop_name",
        "seller__owner_name",
        "seller__user__email",
        "document_number",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25