"""
Тесты для permissions
"""
import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from habits.models import Habit
from habits.permissions.habit_permissions import (
    IsOwner,
    IsOwnerOrReadOnly,
    IsPublicHabitOrOwner,
)
from users.models import User


class TestIsOwnerOrReadOnly:
    """Тесты для IsOwnerOrReadOnly permission"""

    def test_safe_methods_allowed(self, user, habit):
        """Тест: безопасные методы разрешены всем"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user

        permission = IsOwnerOrReadOnly()
        assert permission.has_object_permission(request, None, habit) is True

    def test_write_methods_allowed_for_owner(self, user, habit):
        """Тест: методы записи разрешены владельцу"""
        factory = APIRequestFactory()
        request = factory.put('/')
        request.user = user

        permission = IsOwnerOrReadOnly()
        assert permission.has_object_permission(request, None, habit) is True

    def test_write_methods_denied_for_non_owner(self, db):
        """Тест: методы записи запрещены не владельцу"""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        habit = Habit.objects.create(
            user=user1,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        factory = APIRequestFactory()
        request = factory.put('/')
        request.user = user2

        permission = IsOwnerOrReadOnly()
        assert permission.has_object_permission(request, None, habit) is False


class TestIsOwner:
    """Тесты для IsOwner permission"""

    def test_owner_has_access(self, user, habit):
        """Тест: владелец имеет доступ"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user

        permission = IsOwner()
        assert permission.has_object_permission(request, None, habit) is True

    def test_non_owner_denied(self, db):
        """Тест: не владелец не имеет доступ"""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        habit = Habit.objects.create(
            user=user1,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user2

        permission = IsOwner()
        assert permission.has_object_permission(request, None, habit) is False


class TestIsPublicHabitOrOwner:
    """Тесты для IsPublicHabitOrOwner permission"""

    def test_public_habit_readable_by_all(self, db):
        """Тест: публичная привычка доступна всем для чтения"""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        habit = Habit.objects.create(
            user=user1,
            place='парк',
            time='07:00',
            action='пробежка',
            periodicity=1,
            duration_to_complete=120,
            is_public=True
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user2

        permission = IsPublicHabitOrOwner()
        assert permission.has_object_permission(request, None, habit) is True

    def test_private_habit_readable_only_by_owner(self, db):
        """Тест: приватная привычка доступна только владельцу"""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        habit = Habit.objects.create(
            user=user1,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30,
            is_public=False
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user2

        permission = IsPublicHabitOrOwner()
        assert permission.has_object_permission(request, None, habit) is False

    def test_owner_has_full_access(self, user, habit):
        """Тест: владелец имеет полный доступ"""
        factory = APIRequestFactory()
        request = factory.delete('/')
        request.user = user

        permission = IsPublicHabitOrOwner()
        assert permission.has_object_permission(request, None, habit) is True

    def test_public_habit_not_writable_by_others(self, db):
        """Тест: публичную привычку нельзя редактировать другим"""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        habit = Habit.objects.create(
            user=user1,
            place='парк',
            time='07:00',
            action='пробежка',
            periodicity=1,
            duration_to_complete=120,
            is_public=True
        )

        factory = APIRequestFactory()
        request = factory.put('/')
        request.user = user2

        permission = IsPublicHabitOrOwner()
        assert permission.has_object_permission(request, None, habit) is False
