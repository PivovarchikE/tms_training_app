import factory
from django.utils import timezone

from users.factories import TrainerFactory, UserFactory

from .models import Exercise, TrainingPlan, UserPlanAssignment


class TrainingPlanFactory(factory.django.DjangoModelFactory):
    """Factory for TrainingPlan model."""

    class Meta:
        model = TrainingPlan

    trainer = factory.SubFactory(TrainerFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    is_public = True
    difficulty = TrainingPlan.Difficulty.BEGINNER
    category = TrainingPlan.Category.MIXED
    duration_weeks = factory.Faker("random_int", min=1, max=12)
    sessions_per_week = factory.Faker("random_int", min=1, max=7)


class PrivateTrainingPlanFactory(TrainingPlanFactory):
    """Factory for private TrainingPlan."""

    is_public = False


class ExerciseFactory(factory.django.DjangoModelFactory):
    """Factory for Exercise model."""

    class Meta:
        model = Exercise

    plan = factory.SubFactory(TrainingPlanFactory)
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    muscle_group = Exercise.MuscleGroup.FULL_BODY
    order = factory.Sequence(lambda n: n)
    sets = factory.Faker("random_int", min=1, max=5)
    reps = factory.Faker("random_int", min=5, max=20)
    rest_seconds = factory.Faker("random_int", min=30, max=120)


class TimeBasedExerciseFactory(ExerciseFactory):
    """Factory for time-based Exercise."""

    reps = None
    duration_seconds = factory.Faker("random_int", min=30, max=300)


class UserPlanAssignmentFactory(factory.django.DjangoModelFactory):
    """Factory for UserPlanAssignment model."""

    class Meta:
        model = UserPlanAssignment

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(TrainingPlanFactory)
    assigned_by = factory.SubFactory(TrainerFactory)
    status = UserPlanAssignment.Status.ACTIVE
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    notes = factory.Faker("sentence")
