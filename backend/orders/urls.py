from django.urls import path

from .views import (
    CancelOrderView,
    CheckoutView,
    FarmerOrderDetailView,
    FarmerOrderListView,
    SellerOrderDetailView,
    SellerOrderListView,
    SellerOrderStatusUpdateView,
)

urlpatterns = [
    # Farmer / Buyer
    path(
        "checkout/",
        CheckoutView.as_view(),
        name="checkout",
    ),

    path(
        "my-orders/",
        FarmerOrderListView.as_view(),
        name="my-orders",
    ),

    path(
        "my-orders/<int:order_id>/",
        FarmerOrderDetailView.as_view(),
        name="my-order-detail",
    ),

    path(
        "my-orders/<int:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),

    # Seller
    path(
        "seller/",
        SellerOrderListView.as_view(),
        name="seller-orders",
    ),

    path(
        "seller/<int:order_id>/",
        SellerOrderDetailView.as_view(),
        name="seller-order-detail",
    ),

    path(
        "seller/<int:order_id>/status/",
        SellerOrderStatusUpdateView.as_view(),
        name="seller-order-status",
    ),
]