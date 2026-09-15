from django.urls import path

from .views import (
    CustomerReturnListCreateView,
    CustomerReturnDetailView,
    ReturnProofCreateView,
    CustomerUPIRefundView,
    SellerReturnListView,
    AdminReturnListView,
    AdminReturnReviewView,
    AdminReturnStatusView,
    AdminRefundStatusView,
)


urlpatterns = [

    # Customer
    path(
        "",
        CustomerReturnListCreateView.as_view(),
        name="return-list-create",
    ),

    path(
        "<int:return_id>/",
        CustomerReturnDetailView.as_view(),
        name="return-detail",
    ),

    path(
        "<int:return_id>/proof/",
        ReturnProofCreateView.as_view(),
        name="return-proof-create",
    ),

    path(
        "<int:return_id>/upi/",
        CustomerUPIRefundView.as_view(),
        name="return-upi",
    ),

    # Seller
    path(
        "seller/",
        SellerReturnListView.as_view(),
        name="seller-returns",
    ),

    # Admin
    path(
        "admin/",
        AdminReturnListView.as_view(),
        name="admin-returns",
    ),

    path(
        "admin/<int:return_id>/review/",
        AdminReturnReviewView.as_view(),
        name="admin-return-review",
    ),

    path(
        "admin/<int:return_id>/status/",
        AdminReturnStatusView.as_view(),
        name="admin-return-status",
    ),

    path(
        "admin/<int:return_id>/refund/",
        AdminRefundStatusView.as_view(),
        name="admin-refund-status",
    ),
]