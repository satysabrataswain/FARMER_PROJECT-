from decimal import Decimal

from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from products.models import Product

from .models import Order, OrderItem
from .permissions import IsFarmer, IsSeller
from .serializers import (
    CheckoutSerializer,
    OrderSerializer,
)


class CheckoutView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:
            cart = Cart.objects.select_for_update().get(
                user=request.user
            )
        except Cart.DoesNotExist:
            raise ValidationError(
                "Your cart is empty."
            )

        cart_items = list(
            cart.items.select_related(
                "product",
                "product__seller",
                "product__seller__seller_profile",
            ).select_for_update()
        )

        if not cart_items:
            raise ValidationError(
                "Your cart is empty."
            )

        subtotal = Decimal("0")

        for cart_item in cart_items:
            product = cart_item.product

            if product.status != Product.Status.APPROVED:
                raise ValidationError(
                    f"{product.name} is no longer available."
                )

            if product.stock_quantity < cart_item.quantity:
                raise ValidationError({
                    "stock": (
                        f"Only {product.stock_quantity} "
                        f"{product.unit} of "
                        f"{product.name} is available."
                    )
                })

            if product.seller.role != "SELLER":
                raise ValidationError(
                    f"Seller for {product.name} is invalid."
                )

            try:
                seller_profile = (
                    product.seller.seller_profile
                )
            except Exception:
                raise ValidationError(
                    f"Seller profile for "
                    f"{product.name} is unavailable."
                )

            if (
                seller_profile.verification_status
                != "APPROVED"
            ):
                raise ValidationError(
                    f"Seller for {product.name} "
                    "is not approved."
                )

            subtotal += (
                product.price * cart_item.quantity
            )

        # Delivery charge currently zero.
        # Delivery module can calculate it later.
        delivery_charge = Decimal("0")

        total_amount = (
            subtotal + delivery_charge
        )

        order = Order.objects.create(
            user=request.user,
            receiver_name=data["receiver_name"],
            receiver_phone=data["receiver_phone"],
            state=data["state"],
            district=data["district"],
            village=data.get("village", ""),
            address=data["address"],
            pincode=data["pincode"],
            payment_method=data["payment_method"],
            payment_status=Order.PaymentStatus.PENDING,
            order_status=Order.OrderStatus.PLACED,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            note=data.get("note", ""),
        )

        for cart_item in cart_items:
            product = cart_item.product

            item_total = (
                product.price * cart_item.quantity
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                product_name=product.name,
                product_price=product.price,
                unit=product.unit,
                quantity=cart_item.quantity,
                total_price=item_total,
            )

            product.stock_quantity -= (
                cart_item.quantity
            )

            product.save(
                update_fields=[
                    "stock_quantity",
                    "updated_at",
                ]
            )

        # Cart empty after successful order.
        cart.items.all().delete()

        response_serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class FarmerOrderListView(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(
                user=self.request.user
            )
            .prefetch_related("items")
            .order_by("-created_at")
        )


class FarmerOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    serializer_class = OrderSerializer

    lookup_url_kwarg = "order_id"

    def get_queryset(self):
        return (
            Order.objects.filter(
                user=self.request.user
            )
            .prefetch_related("items")
        )


class SellerOrderListView(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(
                items__seller=self.request.user
            )
            .distinct()
            .prefetch_related("items")
            .order_by("-created_at")
        )


class SellerOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    serializer_class = OrderSerializer

    lookup_url_kwarg = "order_id"

    def get_queryset(self):
        return (
            Order.objects.filter(
                items__seller=self.request.user
            )
            .distinct()
            .prefetch_related("items")
        )


class SellerOrderStatusUpdateView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    ALLOWED_STATUSES = [
        Order.OrderStatus.CONFIRMED,
        Order.OrderStatus.PROCESSING,
        Order.OrderStatus.SHIPPED,
        Order.OrderStatus.OUT_FOR_DELIVERY,
        Order.OrderStatus.DELIVERED,
    ]

    @transaction.atomic
    def patch(self, request, order_id):
        new_status = request.data.get(
            "order_status"
        )

        if new_status not in self.ALLOWED_STATUSES:
            return Response(
                {
                    "detail": (
                        "Invalid order status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.filter(
                id=order_id,
                items__seller=request.user,
            ).distinct().get()
        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Order not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        order.order_status = new_status

        if (
            new_status
            == Order.OrderStatus.DELIVERED
            and order.payment_method
            == Order.PaymentMethod.COD
        ):
            order.payment_status = (
                Order.PaymentStatus.PAID
            )

        order.save()

        serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CancelOrderView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    @transaction.atomic
    def patch(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user,
            )
        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Order not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.order_status not in [
            Order.OrderStatus.PLACED,
            Order.OrderStatus.CONFIRMED,
        ]:
            return Response(
                {
                    "detail": (
                        "This order cannot be "
                        "cancelled now."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.order_status = (
            Order.OrderStatus.CANCELLED
        )
        order.save()

        # Restore stock.
        for item in order.items.select_related(
            "product"
        ):
            product = item.product

            product.stock_quantity += item.quantity

            product.save(
                update_fields=[
                    "stock_quantity",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message": "Order cancelled successfully."
            },
            status=status.HTTP_200_OK,
        )