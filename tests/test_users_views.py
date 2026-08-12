"""
Тесты для views приложения users
"""

import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User


@pytest.mark.django_db
class TestUserViews:
    """Тесты для views пользователей"""

    def test_user_profile_view_get(self, api_client, user):
        """Тест GET запроса профиля пользователя"""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("users:profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email

    def test_user_profile_view_patch(self, api_client, user):
        """Тест PATCH запроса профиля пользователя"""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("users:profile")
        data = {"first_name": "Иван", "last_name": "Иванов"}
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.first_name == "Иван"
        assert user.last_name == "Иванов"

    def test_user_profile_view_put(self, api_client, user):
        """Тест PUT запроса профиля пользователя"""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("users:profile")
        data = {
            "username": user.username,
            "email": "newemail@example.com",
            "first_name": "Петр",
            "last_name": "Петров",
        }
        response = api_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.email == "newemail@example.com"
        assert user.first_name == "Петр"
        assert user.last_name == "Петров"

    def test_user_profile_view_unauthorized(self, api_client):
        """Тест доступа к профилю без авторизации"""
        url = reverse("users:profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_view_creates_user(self, api_client):
        """Тест создания пользователя через register view"""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()

    def test_token_view_returns_tokens(self, api_client, user):
        """Тест получения токена"""
        url = reverse("users:token_obtain_pair")
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_token_view_invalid_credentials(self, api_client, user):
        """Тест получения токена с неверными данными"""
        url = reverse("users:token_obtain_pair")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_profile_update_telegram_chat_id(self, api_client, user):
        """Тест обновления telegram_chat_id"""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("users:profile")
        data = {"telegram_chat_id": "123456789"}
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.telegram_chat_id == "123456789"

    def test_register_view_with_optional_fields(self, api_client):
        """Тест регистрации с дополнительными полями"""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Иван",
            "last_name": "Иванов",
            "telegram_chat_id": "123456",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.get(username="newuser")
        assert user.first_name == "Иван"
        assert user.last_name == "Иванов"
        assert user.telegram_chat_id == "123456"

    def test_register_view_duplicate_username(self, api_client, user):
        """Тест регистрации с существующим username"""
        url = reverse("users:register")
        data = {
            "username": "testuser",  # Уже существует
            "email": "another@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
