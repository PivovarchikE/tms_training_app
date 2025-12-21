from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import (
    NotificationCreateSerializer,
    NotificationListSerializer,
    NotificationSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification model.

    Endpoints:
    - GET /notifications/ - list user's notifications
    - POST /notifications/ - create new notification
    - GET /notifications/{id}/ - retrieve notification
    - DELETE /notifications/{id}/ - delete notification
    - POST /notifications/{id}/read/ - mark as read
    - POST /notifications/read-all/ - mark all as read
    - GET /notifications/unread/ - list unread notifications
    - GET /notifications/unread-count/ - get unread count
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return NotificationCreateSerializer
        elif self.action == "list":
            return NotificationListSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request):
        """Mark all notifications as read."""
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.count()

        for notification in notifications:
            notification.mark_as_read()

        return Response(
            {
                "message": f"Marked {count} notifications as read.",
                "count": count,
            }
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """List unread notifications."""
        queryset = self.get_queryset().filter(is_read=False)
        serializer = NotificationListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=False, methods=["delete"], url_path="clear-read")
    def clear_read(self, request):
        """Delete all read notifications."""
        deleted_count, _ = self.get_queryset().filter(is_read=True).delete()
        return Response(
            {
                "message": f"Deleted {deleted_count} read notifications.",
                "count": deleted_count,
            }
        )
