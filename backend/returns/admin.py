from django.contrib import admin

from .models import (
    ReturnRequest,
    ReturnProof,
)


class ReturnProofInline(admin.TabularInline):

    model = ReturnProof

    extra = 0

    readonly_fields = (
        "captured_at",
        "created_at",
    )


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "order_item",
        "customer",
        "reason",
        "status",
        "suspicious",
        "refund_status",
        "created_at",
    )

    list_filter = (
        "status",
        "reason",
        "suspicious",
        "refund_status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "customer__email",
        "customer__phone",
        "order_item__product_name",
    )

    readonly_fields = (
        "requested_at",
        "approved_at",
        "picked_up_at",
        "received_at",
        "completed_at",
        "created_at",
        "updated_at",
    )

    inlines = [
        ReturnProofInline,
    ]


@admin.register(ReturnProof)
class ReturnProofAdmin(admin.ModelAdmin):

    list_display = (
        "return_request",
        "proof_type",
        "captured_at",
        "latitude",
        "longitude",
    )

    list_filter = (
        "proof_type",
        "captured_at",
    )

    search_fields = (
        "return_request__order__order_number",
    )

    readonly_fields = (
        "captured_at",
        "created_at",
    )