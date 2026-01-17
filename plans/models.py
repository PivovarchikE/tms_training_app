from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TrainingPlan(models.Model):
    """Training plan created by trainer or user."""

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Category(models.TextChoices):
        STRENGTH = "strength", "Strength"
        CARDIO = "cardio", "Cardio"
        FLEXIBILITY = "flexibility", "Flexibility"
        MIXED = "mixed", "Mixed"
        HIIT = "hiit", "HIIT"
        YOGA = "yoga", "Yoga"

    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_plans",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.MIXED,
    )
    duration_weeks = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        help_text="Duration in weeks",
    )
    sessions_per_week = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Training Plan"
        verbose_name_plural = "Training Plans"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def total_exercises(self):
        return self.exercises.count()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 2)
        return None


class UserPlanAssignment(models.Model):
    """Assignment of a training plan to a user by trainer."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_plans",
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        TrainingPlan,
        related_name="assignments",
        on_delete=models.CASCADE,
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="plan_assignments_made",
        on_delete=models.SET_NULL,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Plan Assignment"
        verbose_name_plural = "User Plan Assignments"
        unique_together = ["user", "plan", "start_date"]

    def __str__(self):
        return f"{self.user.username} - {self.plan.title}"


class Exercise(models.Model):
    """Exercise within a training plan."""

    class MuscleGroup(models.TextChoices):
        CHEST = "chest", "Chest"
        BACK = "back", "Back"
        SHOULDERS = "shoulders", "Shoulders"
        BICEPS = "biceps", "Biceps"
        TRICEPS = "triceps", "Triceps"
        LEGS = "legs", "Legs"
        CORE = "core", "Core"
        FULL_BODY = "full_body", "Full Body"
        CARDIO = "cardio", "Cardio"

    plan = models.ForeignKey(
        TrainingPlan,
        related_name="exercises",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    muscle_group = models.CharField(
        max_length=20,
        choices=MuscleGroup.choices,
        default=MuscleGroup.FULL_BODY,
    )
    order = models.PositiveIntegerField(default=0)

    # Exercise parameters
    sets = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )
    reps = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Number of reps (null for time-based exercises)",
    )
    duration_seconds = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Duration in seconds (for time-based exercises)",
    )
    rest_seconds = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(600)],
        help_text="Rest time between sets in seconds",
    )
    target_weight = models.FloatField(
        blank=True,
        null=True,
        help_text="Target weight in kg",
    )

    # Media
    video_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"

    def __str__(self):
        return f"{self.title} ({self.plan.title})"

    @property
    def is_time_based(self):
        return self.duration_seconds is not None and self.reps is None
