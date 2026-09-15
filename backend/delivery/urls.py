from django.urls import path

from .views import (
    DeliveryCreateView,
    DeliveryListView,
    DeliveryDetailView,
    DeliveryStatusUpdateView,
    DeliveryProofUploadView,
    BuyerDeliveryView,
    SellerDeliveryListView,
    CustomerDeliveryConfirmView,
)


urlpatterns = [
    # Admin
    path(
        "",
        DeliveryListView.as_view(),
        name="delivery-list",
    ),

    path(
        "create/",
        DeliveryCreateView.as_view(),
        name="delivery-create",
    ),

    path(
        "<int:delivery_id>/",
        DeliveryDetailView.as_view(),
        name="delivery-detail",
    ),

    path(
        "<int:delivery_id>/status/",
        DeliveryStatusUpdateView.as_view(),
        name="delivery-status-update",
    ),

    path(
        "<int:delivery_id>/proof/",
        DeliveryProofUploadView.as_view(),
        name="delivery-proof-upload",
    ),

    # Buyer
    path(
        "my-order/<int:order_id>/",
        BuyerDeliveryView.as_view(),
        name="buyer-delivery",
    ),

    path(
        "my-order/<int:order_id>/confirm/",
        CustomerDeliveryConfirmView.as_view(),
        name="customer-delivery-confirm",
    ),

    # Seller
    path(
        "seller/",
        SellerDeliveryListView.as_view(),
        name="seller-delivery-list",
    ),
]