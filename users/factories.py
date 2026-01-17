import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for regular User model."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    is_trainer = False
    bio = factory.Faker("paragraph")
    email_verified = False


class TrainerFactory(UserFactory):
    """Factory for Trainer User."""

    is_trainer = True
    bio = factory.Faker("paragraph")


class VerifiedUserFactory(UserFactory):
    """Factory for email-verified User."""

    email_verified = True


class DiaryEntryFactory(factory.django.DjangoModelFactory):
    """Factory for DiaryEntry model."""

    class Meta:
        model = "users.DiaryEntry"

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=5)
    content = factory.Faker("paragraph", nb_sentences=5)
    mood = factory.Faker(
        "random_element",
        elements=["great", "good", "neutral", "bad", "terrible"],
    )
    is_private = True
