from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer
from .permissions import IsAdminUserRole


class MyNotificationListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        notifications = Notification.objects.filter(
            recipient=request.user
        )

        serializer = NotificationSerializer(
            notifications,
            many=True,
        )

        unread_count = notifications.filter(
            is_read=False
        ).count()

        return Response(
            {
                "unread_count": unread_count,
                "notifications": serializer.data,
            }
        )


class NotificationDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, notification_id):

        notification = Notification.objects.filter(
            id=notification_id,
            recipient=request.user,
        ).first()

        if not notification:
            return Response(
                {
                    "detail": (
                        "Notification not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            NotificationSerializer(
                notification
            ).data
        )


class MarkNotificationReadView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(self, request, notification_id):

        notification = Notification.objects.filter(
            id=notification_id,
            recipient=request.user,
        ).first()

        if not notification:
            return Response(
                {
                    "detail": (
                        "Notification not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        notification.is_read = True
        notification.read_at = timezone.now()

        notification.save(
            update_fields=[
                "is_read",
                "read_at",
            ]
        )

        return Response(
            {
                "message": (
                    "Notification marked as read."
                )
            }
        )


class MarkAllNotificationsReadView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(self, request):

        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

        return Response(
            {
                "message": (
                    "All notifications marked as read."
                ),
                "updated_count": updated_count,
            }
        )


class UnreadNotificationCountView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

        return Response(
            {
                "unread_count": count,
            }
        )


class AdminNotificationListView(APIView):

    permission_classes = [
        IsAdminUserRole,
    ]

    def get(self, request):

        notifications = Notification.objects.all()

        serializer = NotificationSerializer(
            notifications,
            many=True,
        )

        return Response(
            serializer.data
        )