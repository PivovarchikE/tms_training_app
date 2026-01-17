import factory
from django.utils import timezone

from users.factories import UserFactory

from .models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for Notification model."""

    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=5)
    body = factory.Faker("paragraph")
    notification_type = Notification.NotificationType.SYSTEM
    priority = Notification.Priority.MEDIUM
    is_read = False
    sent = False


class WorkoutReminderNotificationFactory(NotificationFactory):
    """Factory for workout reminder Notification."""

    notification_type = Notification.NotificationType.WORKOUT_REMINDER
    scheduled_at = factory.LazyFunction(
        lambda: timezone.now() + timezone.timedelta(hours=1)
    )


class SentNotificationFactory(NotificationFactory):
    """Factory for sent Notification."""

    sent = True
    sent_at = factory.LazyFunction(timezone.now)


class ReadNotificationFactory(NotificationFactory):
    """Factory for read Notification."""

    is_read = True
    read_at = factory.LazyFunction(timezone.now)
