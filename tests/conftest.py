"""
Фикстуры для тестов
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from habits.models import Habit

User = get_user_model()


@pytest.fixture
def api_client():
    """API клиент для тестов"""
    return APIClient()


@pytest.fixture
def user(db):
    """Создаёт тестового пользователя"""
    return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def authenticated_client(api_client, user):
    """Аутентифицированный API клиент"""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client, user


@pytest.fixture
def habit(user):
    """Создаёт тестовую привычку"""
    return Habit.objects.create(
        user=user,
        place="дома",
        time="09:00",
        action="попить воды",
        periodicity=1,
        duration_to_complete=30,
        reward="стакан сока",
    )


@pytest.fixture
def pleasant_habit(user):
    """Создаёт приятную привычку"""
    return Habit.objects.create(
        user=user,
        place="дома",
        time="09:05",
        action="посмотреть сериал",
        is_pleasant=True,
        periodicity=1,
        duration_to_complete=60,
    )


@pytest.fixture
def public_habit(db):
    """Создаёт публичную привычку"""
    user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
    return Habit.objects.create(
        user=user,
        place="парк",
        time="07:00",
        action="пробежка",
        periodicity=1,
        duration_to_complete=120,
        is_public=True,
    )
