from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access.
    Roles: guest (anonymous), user (authenticated), trainer (is_trainer=True)
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        TRAINER = "trainer", "Trainer"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    is_trainer = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)

    # Profile dates
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Sync role with is_trainer flag
        if self.is_trainer:
            self.role = self.Role.TRAINER
        super().save(*args, **kwargs)

    @property
    def is_regular_user(self):
        return self.role == self.Role.USER and not self.is_trainer

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class DiaryEntry(models.Model):
    """Personal diary/notes entry for tracking progress and thoughts."""

    class Mood(models.TextChoices):
        GREAT = "great", "Great"
        GOOD = "good", "Good"
        NEUTRAL = "neutral", "Neutral"
        BAD = "bad", "Bad"
        TERRIBLE = "terrible", "Terrible"

    user = models.ForeignKey(
        User,
        related_name="diary_entries",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    mood = models.CharField(
        max_length=20,
        choices=Mood.choices,
        blank=True,
        null=True,
    )
    workout = models.ForeignKey(
        "workouts.WorkoutSession",
        related_name="diary_entries",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: link to a workout session",
    )
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Diary Entry"
        verbose_name_plural = "Diary Entries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
