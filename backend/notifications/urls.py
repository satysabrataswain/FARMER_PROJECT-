from django.urls import path

from .views import (
    MyNotificationListView,
    NotificationDetailView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    UnreadNotificationCountView,
    AdminNotificationListView,
)


urlpatterns = [

    path(
        "",
        MyNotificationListView.as_view(),
        name="my-notifications",
    ),

    path(
        "unread-count/",
        UnreadNotificationCountView.as_view(),
        name="unread-count",
    ),

    path(
        "<int:notification_id>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),

    path(
        "<int:notification_id>/read/",
        MarkNotificationReadView.as_view(),
        name="notification-read",
    ),

    path(
        "read-all/",
        MarkAllNotificationsReadView.as_view(),
        name="notification-read-all",
    ),

    path(
        "admin/",
        AdminNotificationListView.as_view(),
        name="admin-notifications",
    ),
]