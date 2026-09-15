from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .permissions import IsFarmer
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)


def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(
        user=user
    )

    return cart


class CartView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    def get(self, request):
        cart = get_user_cart(request.user)

        serializer = CartSerializer(
            cart,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AddToCartView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    @transaction.atomic
    def post(self, request):
        serializer = AddToCartSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        cart = get_user_cart(request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": quantity,
            },
        )

        if not created:
            new_quantity = (
                cart_item.quantity + quantity
            )

            if new_quantity > product.stock_quantity:
                raise ValidationError({
                    "quantity": (
                        f"Cart quantity cannot exceed "
                        f"available stock "
                        f"({product.stock_quantity})."
                    )
                })

            cart_item.quantity = new_quantity
            cart_item.save()

        response_serializer = CartSerializer(
            cart,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class UpdateCartItemView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    @transaction.atomic
    def patch(self, request, item_id):
        try:
            cart_item = CartItem.objects.select_related(
                "cart",
                "product",
            ).get(
                id=item_id,
                cart__user=request.user,
            )
        except CartItem.DoesNotExist:
            return Response(
                {
                    "detail": "Cart item not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UpdateCartItemSerializer(
            data=request.data,
            context={
                "cart_item": cart_item,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        cart_item.quantity = (
            serializer.validated_data["quantity"]
        )

        cart_item.save()

        cart = cart_item.cart

        response_serializer = CartSerializer(
            cart,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class DeleteCartItemView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    @transaction.atomic
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user,
            )
        except CartItem.DoesNotExist:
            return Response(
                {
                    "detail": "Cart item not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item.delete()

        return Response(
            {
                "message": "Product removed from cart."
            },
            status=status.HTTP_200_OK,
        )


class ClearCartView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFarmer,
    ]

    @transaction.atomic
    def delete(self, request):
        cart = get_user_cart(request.user)

        cart.items.all().delete()

        return Response(
            {
                "message": "Cart cleared successfully."
            },
            status=status.HTTP_200_OK,
        )