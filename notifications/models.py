from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Notification for user reminders and updates."""

    class NotificationType(models.TextChoices):
        WORKOUT_REMINDER = "workout_reminder", "Workout Reminder"
        PLAN_ASSIGNED = "plan_assigned", "Plan Assigned"
        PLAN_COMPLETED = "plan_completed", "Plan Completed"
        NEW_REVIEW = "new_review", "New Review"
        ACHIEVEMENT = "achievement", "Achievement"
        SYSTEM = "system", "System"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    # Scheduling
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)

    # Related objects (optional)
    related_workout = models.ForeignKey(
        "workouts.WorkoutSession",
        related_name="notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    related_plan = models.ForeignKey(
        "plans.TrainingPlan",
        related_name="notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone

        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at", "updated_at"])

    def mark_as_sent(self):
        """Mark notification as sent."""
        from django.utils import timezone

        self.sent = True
        self.sent_at = timezone.now()
        self.save(update_fields=["sent", "sent_at", "updated_at"])
