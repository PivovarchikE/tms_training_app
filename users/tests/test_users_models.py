from django.test import TestCase

from users.factories import TrainerFactory, UserFactory
from users.models import User


class UsersModelsTest(TestCase):
    """
    Tests for User models
    """

    def setUp(self):
        self.user = UserFactory()
        self.trainer = TrainerFactory()

    def test_user_creation(self):
        """
        Test basic user creation
        """

        self.assertIsInstance(self.user, User)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_trainer)
        self.assertIsNotNone(self.user.pk)

    def test_trainer_creation(self):
        """Test basic trainer creation"""
        self.assertIsInstance(self.trainer, User)
        self.assertIsNotNone(self.trainer.pk)
        self.assertFalse(self.trainer.is_staff)
        self.assertTrue(self.trainer.is_trainer)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = UserFactory(username="test_user")
        self.assertEqual(str(user), "test_user")

    def test_trainer_str_representation(self):
        """Test trainer string representation"""
        trainer = TrainerFactory(username="test_trainer")
        self.assertEqual(str(trainer), "test_trainer")


class UserPropertiesTestCase(TestCase):
    """Test properties of User model"""

    def test_full_name_with_first_name_and_last_name(self):
        """Test full name with first name and last name"""
        user = UserFactory(first_name="John", last_name="Doe")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.full_name, "John Doe")

    def test_full_name_without_last_name(self):
        """Test full name with no last name"""
        user = UserFactory(first_name="John", last_name="")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "")
        self.assertEqual(user.full_name, "John")


class UserAuthTestCase(TestCase):
    """Test authentication of User model"""

    def test_user_password_is_hashed(self):
        """Test user password hashing"""
        user = UserFactory(password="1234")
        self.assertNotEqual(user.password, "1234")
        self.assertTrue(user.check_password("1234"))

    def test_user_can_authenticate(self):
        """Test user can authenticate"""
        user = UserFactory(password="1234")
        self.assertTrue(user.check_password("1234"))

    def test_user_cannot_authenticate(self):
        """Test user cannot authenticate"""
        user = UserFactory(password="1234")
        self.assertFalse(user.check_password("123"))
