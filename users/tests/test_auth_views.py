import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.factories import TrainerFactory, UserFactory
from users.models import User


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def authenticated_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def trainer_client(api_client):
    trainer = TrainerFactory()
    api_client.force_authenticate(user=trainer)
    return api_client, trainer


@pytest.mark.django_db
class TestRegistration:
    """Test for user registration endpoint"""

    def test_register_success(self, api_client):
        """Test user registration success"""
        url = reverse("auth:register")
        data = {
            "username": "testuser",
            "email": "test@test.by",
            "password": "1234Ffdkl",
            "password_confirm": "1234Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": False,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert response.data["user"]["username"] == "testuser"
        assert User.objects.filter(username="testuser").exists()

    def test_register_password_mismatch(self, api_client):
        """Test registration fails when password don't mismatch"""

        url = reverse("auth:register")
        data = {
            "username": "testuser",
            "email": "test@test.by",
            "password": "1234Ffdkl",
            "password_confirm": "123Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": False,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_duplicate_email(self, api_client):
        """Test user registration fails when email already exists"""
        url = reverse("auth:register")
        UserFactory(email="test1@mail.com")

        data = {
            "username": "test1@mail.com",
            "email": "test1@mail.com",
            "password": "1234Ffdkl",
            "password_confirm": "123Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": False,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_duplicate_username(self, api_client):
        """Test user registration fails when username already exists"""
        url = reverse("auth:register")
        UserFactory(username="test1")

        data = {
            "username": "test1",
            "email": "test2@mail.com",
            "password": "1234Ffdkl",
            "password_confirm": "123Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": False,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_register_as_trainer(self, api_client):
        """Test registration as a trainer"""
        url = reverse("auth:register")

        data = {
            "username": "test1",
            "email": "test3@mail.com",
            "password": "1234Ffdkl",
            "password_confirm": "1234Ffdkl",
            "first_name": "test",
            "last_name": "test",
            "is_trainer": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["is_trainer"] is True


@pytest.mark.django_db
class TestAuthenticatedAccess:
    """Test for authenticated access"""

    def test_logout_authenticated(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("auth:logout")

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Logout successful."

    def test_get_current_user_authenticated(self, authenticated_client):
        """Test authenticated user can get their profile"""
        client, user = authenticated_client
        url = reverse("user-me")

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email

    def test_get_current_user_not_authenticated(self, api_client):
        """Test not authenticated user can't get their profile"""
        url = reverse("user-me")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
