from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Review for a training plan."""

    plan = models.ForeignKey(
        "plans.TrainingPlan",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5",
    )
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)

    # Moderation
    is_approved = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        unique_together = ["plan", "user"]

    def __str__(self):
        return f"Review by {self.user.username} for {self.plan.title}"

    def clean(self):
        """Validate review constraints."""
        super().clean()
        # User cannot review their own plan
        if self.plan and self.plan.trainer == self.user:
            raise ValidationError("You cannot review your own training plan.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TrainerReview(models.Model):
    """Review for a trainer."""

    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="trainer_reviews",
        on_delete=models.CASCADE,
        limit_choices_to={"is_trainer": True},
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="given_trainer_reviews",
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5",
    )
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)

    # Moderation
    is_approved = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trainer Review"
        verbose_name_plural = "Trainer Reviews"
        ordering = ["-created_at"]
        unique_together = ["trainer", "user"]

    def __str__(self):
        return f"Review by {self.user.username} for trainer {self.trainer.username}"

    def clean(self):
        """Validate review constraints."""
        super().clean()
        # User cannot review themselves
        if self.trainer == self.user:
            raise ValidationError("You cannot review yourself.")
        # Trainer must be an actual trainer
        if self.trainer and not self.trainer.is_trainer:
            raise ValidationError("You can only review trainers.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
