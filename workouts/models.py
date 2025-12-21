from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class WorkoutSession(models.Model):
    """A workout session recorded by user."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        SKIPPED = "skipped", "Skipped"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="workout_sessions",
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        "plans.TrainingPlan",
        related_name="workout_sessions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: link to a training plan",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Scheduling
    scheduled_date = models.DateTimeField(
        help_text="When the workout is scheduled",
    )
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Duration
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(600)],
        help_text="Duration in minutes",
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    # Additional info
    notes = models.TextField(blank=True)
    calories_burned = models.PositiveIntegerField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User's rating of the workout (1-5)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workout Session"
        verbose_name_plural = "Workout Sessions"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def start_workout(self):
        """Start the workout session."""
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_at"])

    def complete_workout(self):
        """Complete the workout session."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
        self.save(
            update_fields=["status", "completed_at", "duration_minutes", "updated_at"]
        )

    def cancel_workout(self):
        """Cancel the workout session."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])

    def skip_workout(self):
        """Mark workout as skipped."""
        self.status = self.Status.SKIPPED
        self.save(update_fields=["status", "updated_at"])

    @property
    def is_upcoming(self):
        return (
            self.status == self.Status.SCHEDULED
            and self.scheduled_date > timezone.now()
        )

    @property
    def total_exercises(self):
        return self.exercise_results.count()

    @property
    def completed_exercises(self):
        return self.exercise_results.filter(completed=True).count()


class ExerciseResult(models.Model):
    """Result of an exercise performed during a workout session."""

    session = models.ForeignKey(
        WorkoutSession,
        related_name="exercise_results",
        on_delete=models.CASCADE,
    )
    exercise = models.ForeignKey(
        "plans.Exercise",
        related_name="results",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # Custom exercise name if not linked to plan exercise
    exercise_name = models.CharField(max_length=200, blank=True)

    # Performance metrics
    sets_completed = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(50)],
    )
    reps = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1000)],
        help_text="Total reps or reps per set",
    )
    weight = models.FloatField(
        null=True,
        blank=True,
        help_text="Weight in kg",
    )
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration in seconds (for time-based exercises)",
    )
    distance_meters = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Distance in meters (for cardio exercises)",
    )

    # Status
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exercise Result"
        verbose_name_plural = "Exercise Results"
        ordering = ["created_at"]

    def __str__(self):
        name = self.exercise.title if self.exercise else self.exercise_name
        return f"{name} - {self.session}"

    def get_exercise_name(self):
        """Return exercise name from linked exercise or custom name."""
        if self.exercise:
            return self.exercise.title
        return self.exercise_name

    @property
    def total_volume(self):
        """Calculate total volume (sets * reps * weight)."""
        if all([self.sets_completed, self.reps, self.weight]):
            return self.sets_completed * self.reps * self.weight
        return None
