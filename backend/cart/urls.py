from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    ClearCartView,
    DeleteCartItemView,
    UpdateCartItemView,
)

urlpatterns = [
    path(
        "",
        CartView.as_view(),
        name="cart",
    ),

    path(
        "add/",
        AddToCartView.as_view(),
        name="cart-add",
    ),

    path(
        "items/<int:item_id>/",
        UpdateCartItemView.as_view(),
        name="cart-item-update",
    ),

    path(
        "items/<int:item_id>/delete/",
        DeleteCartItemView.as_view(),
        name="cart-item-delete",
    ),

    path(
        "clear/",
        ClearCartView.as_view(),
        name="cart-clear",
    ),
]