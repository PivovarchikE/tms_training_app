import factory

from plans.factories import TrainingPlanFactory
from users.factories import TrainerFactory, UserFactory

from .models import Review, TrainerReview


class ReviewFactory(factory.django.DjangoModelFactory):
    """Factory for Review model."""

    class Meta:
        model = Review

    plan = factory.SubFactory(TrainingPlanFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker("random_int", min=1, max=5)
    title = factory.Faker("sentence", nb_words=5)
    text = factory.Faker("paragraph")
    is_approved = True


class TrainerReviewFactory(factory.django.DjangoModelFactory):
    """Factory for TrainerReview model."""

    class Meta:
        model = TrainerReview

    trainer = factory.SubFactory(TrainerFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker("random_int", min=1, max=5)
    title = factory.Faker("sentence", nb_words=5)
    text = factory.Faker("paragraph")
    is_approved = True
