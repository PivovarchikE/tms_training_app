"""
Celery tasks for Users app

Tasks:
    - send_verification_email
    - send_weekly_report (scheduled)
    - cleanup_unverified_users (scheduled)
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_verification_email(self, user_id):
    """
    Send verification email to user
    """

    from users.models import User

    logger.info(f'[Task {self.request.id}] Sending verification email to {user_id}]')

    try:
        user = User.objects.get(id=user_id)

        if user.email_verified:
            logger.info(f'[Task {self.request.id}] Email already verified')
            return {'status': 'skipped', 'reason': 'Email already verified'}

        if not user.email_verification_token:
            logger.info(f'User {user_id} has no email verification token')
            return {'status': 'error', 'reason': 'User has no email verification token'}

        verification_link = f'{settings.FRONTEND_URL}/verify-email/{user.email_verification_token}'

        send_mail(
            subject='Training App: Verify your email',
            message=f'Verify your email: {verification_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f'[Task {self.request.id}] Email sent to {user.email}')

        return {'status': 'success', 'reason': f'Email sent to {user.email}'}

    except User.DoesNotExist:
        logger.info(f'[Task {self.request.id}] User does not exist')
        return {'status': 'error', 'reason': 'User does not exist'}

    except Exception as exc:
        logger.info(f'[Task {self.request.id}] Exception: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True)
def send_weekly_report(self):
    from users.models import User
    from workouts.models import WorkoutSession

    logger.info(f'[Task {self.request.id}] Sending weekly report')

    week_ago = timezone.now() - timedelta(days=7)

    users = User.objects.filter(is_active=True, email_verified=True).exclude(email='')

    sent_count = 0

    for user in users:
        stats = WorkoutSession.objects.filter(user=user, created_at__gte=week_ago).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(stats='completed')),
            duration=Sum('duration_minutes'),
            calories=Sum('calories_burned')
        )

        if stats['total'] and stats['total'] > 0:
            completion_rate = (stats['completed'] or 0) / stats['total'] * 100

            message = f"""
        Hello, {user.email}!
        Count of trainings: {stats['completed']}
        Completion rate: {completion_rate}%
        Duration: {stats['duration']}
        Calories: {stats['calories']}
        """

        try:
            send_mail(
                subject='Training App: Weekly report',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception as exc:
            logger.error(f'[Task {self.request.id}] Exception: {exc}. Failed to send weekly report to {user.email}')

    logger.info(f'[Task {self.request.id}] Finished sending weekly report]')
    logger.info(f'[Task {self.request.id}] Sent {sent_count} weekly reports')

    return {'status': 'success', 'sent_count': sent_count, 'total_users': len(users)}


@shared_task(bind=True)
def cleanup_unverified_users(self):
    from users.models import User

    logger.info(f'[Task {self.request.id}] Cleaning up verified users')

    threshold = timezone.now() - timedelta(days=7)
    unverified = User.objects.filter(email_verified=False, created_at__gte=threshold)

    count = unverified.count()

    if count > 0:
        usernames = list(unverified.values_list('username', flat=True)[:10])
        logger.info(f"Deleting {count} unverified users: {usernames}")

        deleted_count, _ = unverified.delete()

        logger.info(f"Task {self.request.id}: Deleted {deleted_count} unverified users")

        return {
            'status': 'success',
            'deleted_count': deleted_count,
        }

    logger.info(f"[Task {self.request.id}] No users to cleanup")
    return {
        'status': 'success',
        'deleted_count': 0
    }
