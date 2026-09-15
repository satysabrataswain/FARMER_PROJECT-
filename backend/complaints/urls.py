
from django.urls import path

from .views import (
    CustomerComplaintListCreateView,
    CustomerComplaintDetailView,
    CustomerComplaintMessageView,
    CustomerComplaintAttachmentView,
    SellerComplaintListView,
    SellerComplaintMessageView,
    SellerComplaintAttachmentView,
    AdminComplaintListView,
    AdminComplaintDetailView,
    AdminComplaintStatusView,
    AdminComplaintMessageView,
    AdminInternalComplaintMessageView,
    AdminComplaintAttachmentView,
)


urlpatterns = [

    # ========================================================
    # CUSTOMER / BUYER
    # ========================================================

    path(
        "",
        CustomerComplaintListCreateView.as_view(),
        name="customer-complaint-list-create",
    ),

    path(
        "<int:complaint_id>/",
        CustomerComplaintDetailView.as_view(),
        name="customer-complaint-detail",
    ),

    path(
        "<int:complaint_id>/message/",
        CustomerComplaintMessageView.as_view(),
        name="customer-complaint-message",
    ),

    path(
        "<int:complaint_id>/attachment/",
        CustomerComplaintAttachmentView.as_view(),
        name="customer-complaint-attachment",
    ),


    # ========================================================
    # SELLER
    # ========================================================

    path(
        "seller/",
        SellerComplaintListView.as_view(),
        name="seller-complaint-list",
    ),

    path(
        "seller/<int:complaint_id>/message/",
        SellerComplaintMessageView.as_view(),
        name="seller-complaint-message",
    ),

    path(
        "seller/<int:complaint_id>/attachment/",
        SellerComplaintAttachmentView.as_view(),
        name="seller-complaint-attachment",
    ),


    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/",
        AdminComplaintListView.as_view(),
        name="admin-complaint-list",
    ),

    path(
        "admin/<int:complaint_id>/",
        AdminComplaintDetailView.as_view(),
        name="admin-complaint-detail",
    ),

    path(
        "admin/<int:complaint_id>/status/",
        AdminComplaintStatusView.as_view(),
        name="admin-complaint-status",
    ),

    path(
        "admin/<int:complaint_id>/message/",
        AdminComplaintMessageView.as_view(),
        name="admin-complaint-message",
    ),

    path(
        "admin/<int:complaint_id>/internal-message/",
        AdminInternalComplaintMessageView.as_view(),
        name="admin-internal-complaint-message",
    ),

    path(
        "admin/<int:complaint_id>/attachment/",
        AdminComplaintAttachmentView.as_view(),
        name="admin-complaint-attachment",
    ),
]
