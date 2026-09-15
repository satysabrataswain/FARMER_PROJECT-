from django.urls import path

from .views import (
    AdminProductVerificationDetailView,
    AdminProductVerificationListView,
    BuyerProductDetailView,
    BuyerProductListView,
    SellerProductDetailView,
    SellerProductListCreateView,
    ProductImageUploadView,
    SellerProductVideoDeleteView,
    SellerProductVideoView,
)

urlpatterns = [
    # Seller
    path(
        "seller/",
        SellerProductListCreateView.as_view(),
        name="seller-product-list-create",
    ),
    path(
        "seller/<int:product_id>/",
        SellerProductDetailView.as_view(),
        name="seller-product-detail",
    ),
    path(
        "seller/<int:product_id>/images/",
        ProductImageUploadView.as_view(),
        name="seller-product-image-upload",
    ),
    path(
        "seller/<int:product_id>/video/",
        SellerProductVideoView.as_view(),
        name="seller-product-video-upload",
    ),
    path(
        "seller/video/<int:video_id>/",
        SellerProductVideoDeleteView.as_view(),
        name="seller-product-video-delete",
    ),

    # Buyer
    path(
        "",
        BuyerProductListView.as_view(),
        name="buyer-product-list",
    ),
    path(
        "<int:product_id>/",
        BuyerProductDetailView.as_view(),
        name="buyer-product-detail",
    ),

    # Admin
    path(
        "verification/",
        AdminProductVerificationListView.as_view(),
        name="admin-product-verification-list",
    ),
    path(
        "verification/<int:product_id>/",
        AdminProductVerificationDetailView.as_view(),
        name="admin-product-verification-detail",
    ),
]