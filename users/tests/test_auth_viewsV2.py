from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.factories import UserFactory
from users.models import User


class TestRegistration(TestCase):
    """Test for user registration endpoint"""

    def setUp(self):
        # Если from rest_framework.test import APITestCase, то дальше можно юзать self.client без создания этого клиента
        # self.client = APIClient()
        self.url = reverse("auth:register")

    def test_register_success(self):
        """Test user registration success"""
        data = {
            "username": "testuser",
            "email": "test@test.by",
            "password": "1234Ffdkl",
            "password_confirm": "1234Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": False,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert "tokens" in response.data
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["username"], "testuser")
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_password_mismatch(self):
        """Test registration fails when password don't mismatch"""

        data = {
            "username": "testuser",
            "email": "test@test.by",
            "password": "1234Ffdkl",
            "password_confirm": "123Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": False,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)


class TestAuthenticatedAccess(APITestCase):
    """Test for authenticated access"""

    def test_logout_authenticated(self):
        user = UserFactory()
        self.client.force_authenticate(user)
        url = reverse("auth:logout")

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful.")

    def test_get_current_user_authenticated(self):
        """Test authenticated user can get their profile"""
        user = UserFactory()
        self.client.force_authenticate(user)
        url = reverse("user-me")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["email"], user.email)
