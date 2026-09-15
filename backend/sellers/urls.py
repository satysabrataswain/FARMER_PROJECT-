from django.urls import path

from .views import (
    SellerDocumentDetailView,
    SellerDocumentListForAdminView,
    SellerDocumentVerificationDetailView,
    SellerDocumentView,
    SellerProfileView,
    SellerVerificationDetailView,
    SellerVerificationListView,
)


urlpatterns = [
    # Seller Profile
    path(
        "profile/",
        SellerProfileView.as_view(),
        name="seller-profile",
    ),

    # Seller Documents
    path(
        "documents/",
        SellerDocumentView.as_view(),
        name="seller-documents",
    ),

    path(
        "documents/<int:document_id>/",
        SellerDocumentDetailView.as_view(),
        name="seller-document-detail",
    ),

    # Admin Seller Verification
    path(
        "verification/",
        SellerVerificationListView.as_view(),
        name="seller-verification-list",
    ),

    path(
        "verification/<int:seller_id>/",
        SellerVerificationDetailView.as_view(),
        name="seller-verification-detail",
    ),

    # Admin Document Verification
    path(
        "verification/documents/",
        SellerDocumentListForAdminView.as_view(),
        name="seller-document-list-admin",
    ),

    path(
        "verification/documents/<int:document_id>/",
        SellerDocumentVerificationDetailView.as_view(),
        name="seller-document-verification-detail",
    ),
]