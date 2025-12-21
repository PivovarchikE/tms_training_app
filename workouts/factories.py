import factory
from django.utils import timezone

from plans.factories import ExerciseFactory, TrainingPlanFactory
from users.factories import UserFactory

from .models import ExerciseResult, WorkoutSession


class WorkoutSessionFactory(factory.django.DjangoModelFactory):
    """Factory for WorkoutSession model."""

    class Meta:
        model = WorkoutSession

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(TrainingPlanFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    scheduled_date = factory.LazyFunction(timezone.now)
    status = WorkoutSession.Status.SCHEDULED
    notes = factory.Faker("sentence")


class CompletedWorkoutSessionFactory(WorkoutSessionFactory):
    """Factory for completed WorkoutSession."""

    status = WorkoutSession.Status.COMPLETED
    started_at = factory.LazyFunction(
        lambda: timezone.now() - timezone.timedelta(hours=1)
    )
    completed_at = factory.LazyFunction(timezone.now)
    duration_minutes = 60
    rating = factory.Faker("random_int", min=1, max=5)


class InProgressWorkoutSessionFactory(WorkoutSessionFactory):
    """Factory for in-progress WorkoutSession."""

    status = WorkoutSession.Status.IN_PROGRESS
    started_at = factory.LazyFunction(timezone.now)


class ExerciseResultFactory(factory.django.DjangoModelFactory):
    """Factory for ExerciseResult model."""

    class Meta:
        model = ExerciseResult

    session = factory.SubFactory(WorkoutSessionFactory)
    exercise = factory.SubFactory(ExerciseFactory)
    sets_completed = factory.Faker("random_int", min=1, max=5)
    reps = factory.Faker("random_int", min=5, max=20)
    weight = factory.Faker("pyfloat", min_value=5, max_value=100, right_digits=1)
    completed = False
    notes = factory.Faker("sentence")


class CompletedExerciseResultFactory(ExerciseResultFactory):
    """Factory for completed ExerciseResult."""

    completed = True


class CardioExerciseResultFactory(ExerciseResultFactory):
    """Factory for cardio ExerciseResult."""

    reps = None
    weight = None
    duration_seconds = factory.Faker("random_int", min=300, max=3600)
    distance_meters = factory.Faker("random_int", min=500, max=10000)
