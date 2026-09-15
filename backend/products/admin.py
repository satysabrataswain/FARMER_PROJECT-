from django.contrib import admin

from .models import Product, ProductImage, ProductVideo


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductVideoInline(admin.StackedInline):
    model = ProductVideo
    extra = 0
    max_num = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "seller",
        "price",
        "stock_quantity",
        "status",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "brand",
        "sku",
        "seller__email",
        "seller__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        ProductImageInline,
        ProductVideoInline,
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "display_order",
        "created_at",
    )

    search_fields = (
        "product__name",
    )


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "created_at",
    )

    search_fields = (
        "product__name",
    )