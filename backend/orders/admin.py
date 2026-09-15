from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "seller",
        "product_name",
        "product_price",
        "unit",
        "quantity",
        "total_price",
        "created_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "payment_method",
        "payment_status",
        "order_status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__email",
        "user__name",
        "receiver_name",
        "receiver_phone",
    )

    readonly_fields = (
        "order_number",
        "user",
        "subtotal",
        "delivery_charge",
        "total_amount",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "seller",
        "quantity",
        "total_price",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "product_name",
        "seller__email",
    )

    readonly_fields = (
        "order",
        "product",
        "seller",
        "product_name",
        "product_price",
        "unit",
        "quantity",
        "total_price",
        "created_at",
    )