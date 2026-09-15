from decimal import Decimal

from rest_framework import serializers

from products.models import Product

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    product_unit = serializers.CharField(
        source="product.unit",
        read_only=True,
    )

    product_image = serializers.SerializerMethodField()

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "product_unit",
            "product_image",
            "quantity",
            "total_price",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "product_price",
            "product_unit",
            "product_image",
            "total_price",
            "created_at",
            "updated_at",
        ]

    def get_product_image(self, obj):
        image = obj.product.images.first()

        if not image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                image.image.url
            )

        return image.image.url

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )

    total_items = serializers.SerializerMethodField()

    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total_items",
            "cart_total",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_total_items(self, obj):
        total = Decimal("0")

        for item in obj.items.all():
            total += item.quantity

        return total

    def get_cart_total(self, obj):
        total = Decimal("0")

        for item in obj.items.all():
            total += item.product.price * item.quantity

        return total


class AddToCartSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )

    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    def validate_product(self, product):
        if product.status != Product.Status.APPROVED:
            raise serializers.ValidationError(
                "This product is not available for purchase."
            )

        if product.seller.role != "SELLER":
            raise serializers.ValidationError(
                "This product seller is invalid."
            )

        try:
            seller_profile = product.seller.seller_profile
        except Exception:
            raise serializers.ValidationError(
                "Seller profile is not available."
            )

        if seller_profile.verification_status != "APPROVED":
            raise serializers.ValidationError(
                "This seller is not approved."
            )

        if product.stock_quantity <= 0:
            raise serializers.ValidationError(
                "This product is out of stock."
            )

        return product

    def validate(self, attrs):
        product = attrs["product"]
        quantity = attrs["quantity"]

        if quantity > product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": (
                    f"Only {product.stock_quantity} "
                    f"{product.unit} is available."
                )
            })

        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    def validate(self, attrs):
        cart_item = self.context["cart_item"]

        quantity = attrs["quantity"]

        if quantity > cart_item.product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": (
                    f"Only {cart_item.product.stock_quantity} "
                    f"{cart_item.product.unit} is available."
                )
            })

        if cart_item.product.status != Product.Status.APPROVED:
            raise serializers.ValidationError(
                "This product is no longer available."
            )

        return attrs