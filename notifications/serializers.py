from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "title",
            "body",
            "notification_type",
            "priority",
            "is_read",
            "read_at",
            "scheduled_at",
            "sent",
            "sent_at",
            "related_workout",
            "related_plan",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "is_read",
            "read_at",
            "sent",
            "sent_at",
            "created_at",
            "updated_at",
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Notification."""

    class Meta:
        model = Notification
        fields = [
            "title",
            "body",
            "notification_type",
            "priority",
            "scheduled_at",
            "related_workout",
            "related_plan",
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing Notifications."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "notification_type",
            "priority",
            "is_read",
            "created_at",
        ]
