from django.contrib import admin

from .models import Delivery, DeliveryProof


class DeliveryProofInline(admin.TabularInline):
    model = DeliveryProof
    extra = 0
    readonly_fields = (
        "captured_at",
        "created_at",
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "tracking_number",
        "delivery_partner_name",
        "status",
        "customer_otp_verified",
        "estimated_delivery_date",
        "created_at",
    )

    list_filter = (
        "status",
        "customer_otp_verified",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "tracking_number",
        "delivery_partner_name",
        "delivery_partner_phone",
    )

    readonly_fields = (
        "picked_up_at",
        "delivered_at",
        "customer_otp_verified",
        "customer_otp_verified_at",
        "created_at",
        "updated_at",
    )

    inlines = [
        DeliveryProofInline,
    ]


@admin.register(DeliveryProof)
class DeliveryProofAdmin(admin.ModelAdmin):
    list_display = (
        "delivery",
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
        "delivery__order__order_number",
    )

    readonly_fields = (
        "captured_at",
        "created_at",
    )