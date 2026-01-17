from django.test import TestCase

from users.factories import UserFactory
from users.serializers import UserSerializer


class UserSerializerTestCasE(TestCase):
    def setUp(self):
        self.user = UserFactory(
            username="testuser", email="123@mail.com", bio="test bio"
        )

    def test_user_serializer(self):
        """Test serializer a user"""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["id"], self.user.pk)
        self.assertEqual(data["email"], "123@mail.com")
        self.assertEqual(data["bio"], "test bio")
        self.assertEqual(data["full_name"], f'{data["first_name"]} {data["last_name"]}')
