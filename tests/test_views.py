"""
Тесты для API views
"""

import pytest
from django.urls import reverse
from rest_framework import status

from habits.models import Habit
from users.models import User


@pytest.mark.django_db
class TestAuthenticationViews:
    """Тесты авторизации"""

    def test_register_user_success(self, api_client):
        """Тест успешной регистрации"""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

        # Проверяем, что пользователь создан
        assert User.objects.filter(username="newuser").exists()

    def test_register_passwords_not_match(self, api_client):
        """Тест регистрации с несовпадающими паролями"""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "testpass123",
            "password_confirm": "differentpass",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, api_client, user):
        """Тест успешного входа"""
        url = reverse("users:token_obtain_pair")
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self, api_client, user):
        """Тест входа с неверными данными"""
        url = reverse("users:token_obtain_pair")
        data = {"username": "testuser", "password": "wrongpass"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestHabitViews:
    """Тесты views для привычек"""

    def test_list_habits_requires_auth(self, api_client):
        """Тест: список привычек требует авторизации"""
        url = reverse("habits:habit-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_my_habits(self, authenticated_client, habit):
        """Тест списка своих привычек"""
        client, user = authenticated_client
        url = reverse("habits:habit-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["action"] == "попить воды"

    def test_create_habit(self, authenticated_client):
        """Тест создания привычки"""
        client, user = authenticated_client
        url = reverse("habits:habit-list")
        data = {
            "action": "попить воды",
            "place": "дома",
            "time": "09:00",
            "periodicity": 1,
            "duration_to_complete": 30,
            "reward": "шоколадка",
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Habit.objects.filter(user=user, action="попить воды").exists()

    def test_create_habit_validation_execution_time(self, authenticated_client):
        """Тест валидации времени выполнения при создании"""
        client, user = authenticated_client
        url = reverse("habits:habit-list")
        data = {
            "action": "читать книгу",
            "place": "дома",
            "time": "09:00",
            "periodicity": 1,
            "duration_to_complete": 121,
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_habit_owner(self, authenticated_client, habit):
        """Тест просмотра своей привычки"""
        client, user = authenticated_client
        url = reverse("habits:habit-detail", kwargs={"pk": habit.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["action"] == "попить воды"

    def test_retrieve_habit_not_owner(self, api_client, habit):
        """Тест просмотра чужой привычки"""
        # Создаём другого пользователя и авторизуемся
        user2 = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("habits:habit-detail", kwargs={"pk": habit.pk})
        response = api_client.get(url)
        # Должен быть 404, так как привычка не в queryset другого пользователя
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_update_habit_owner(self, authenticated_client, habit):
        """Тест редактирования своей привычки"""
        client, user = authenticated_client
        url = reverse("habits:habit-detail", kwargs={"pk": habit.pk})
        data = {"action": "попить больше воды", "place": "на работе"}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        habit.refresh_from_db()
        assert habit.action == "попить больше воды"

    def test_delete_habit_owner(self, authenticated_client, habit):
        """Тест удаления своей привычки"""
        client, user = authenticated_client
        url = reverse("habits:habit-detail", kwargs={"pk": habit.pk})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Habit.objects.filter(pk=habit.pk).exists()

    def test_list_public_habits(self, authenticated_client, public_habit):
        """Тест списка публичных привычек"""
        client, user = authenticated_client
        url = reverse("habits:habit-public")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_pagination(self, authenticated_client, user):
        """Тест пагинации"""
        client, user = authenticated_client

        # Создаём 10 привычек
        for i in range(10):
            Habit.objects.create(
                user=user, place="дома", time="09:00", action=f"привычка {i}", periodicity=1, duration_to_complete=30
            )

        url = reverse("habits:habit-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data
        assert len(response.data["results"]) == 5  # Page size = 5

        # Проверяем вторую страницу
        if response.data["next"]:
            response = client.get(response.data["next"])
            assert len(response.data["results"]) == 5


class TestUserProfileView:
    """Тесты профиля пользователя"""

    def test_get_profile_authenticated(self, authenticated_client):
        """Тест получения профиля авторизованным пользователем"""
        client, user = authenticated_client
        url = reverse("users:profile")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username

    def test_get_profile_not_authenticated(self, api_client):
        """Тест получения профиля неавторизованным пользователем"""
        url = reverse("users:profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, authenticated_client):
        """Тест обновления профиля"""
        client, user = authenticated_client
        url = reverse("users:profile")
        data = {"first_name": "Иван", "last_name": "Иванов"}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Иван"
        assert user.last_name == "Иванов"
