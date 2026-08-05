"""
Тесты для сериализаторов
"""
import pytest
from rest_framework.serializers import ErrorDetail

from habits.models import Habit
from habits.serializers.habit_serializers import (
    HabitCreateSerializer,
    HabitDetailSerializer,
    HabitListSerializer,
    HabitUpdateSerializer,
)
from users.serializers import RegisterSerializer


class TestHabitSerializers:
    """Тесты сериализаторов привычек"""

    def test_habit_list_serializer(self, habit):
        """Тест сериализатора списка привычек"""
        serializer = HabitListSerializer(habit)
        data = serializer.data

        assert data['id'] == habit.id
        assert data['action'] == habit.action
        assert data['place'] == habit.place
        assert data['time'] == str(habit.time)
        assert 'username' in data
        assert data['username'] == habit.user.username

    def test_habit_detail_serializer(self, habit):
        """Тест детального сериализатора"""
        serializer = HabitDetailSerializer(habit)
        data = serializer.data

        assert data['id'] == habit.id
        assert data['action'] == habit.action
        assert data['place'] == habit.place
        assert data['reward'] == habit.reward

    def test_habit_create_serializer_valid(self, user):
        """Тест сериализатора создания с валидными данными"""
        data = {
            'action': 'попить воды',
            'place': 'дома',
            'time': '09:00',
            'periodicity': 1,
            'duration_to_complete': 30,
            'reward': 'шоколадка'
        }
        serializer = HabitCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        habit = serializer.save(user=user)
        assert habit.action == 'попить воды'
        assert habit.user == user

    def test_habit_create_serializer_reward_and_related_mutually_exclusive(
        self, user, pleasant_habit
    ):
        """Тест: нельзя указывать reward и related_habit одновременно"""
        data = {
            'action': 'попить воды',
            'place': 'дома',
            'time': '09:00',
            'periodicity': 1,
            'duration_to_complete': 30,
            'reward': 'шоколадка',
            'related_habit': pleasant_habit.id
        }
        serializer = HabitCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors or '__all__' in serializer.errors

    def test_habit_create_serializer_execution_time_exceeded(self, user):
        """Тест: время выполнения не может превышать 120 секунд"""
        data = {
            'action': 'читать книгу',
            'place': 'дома',
            'time': '09:00',
            'periodicity': 1,
            'duration_to_complete': 121
        }
        serializer = HabitCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert '120' in str(serializer.errors)

    def test_habit_create_serializer_periodicity_validation(self, user):
        """Тест: периодичность от 1 до 7"""
        data = {
            'action': 'попить воды',
            'place': 'дома',
            'time': '09:00',
            'periodicity': 8,
            'duration_to_complete': 30
        }
        serializer = HabitCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_habit_update_serializer(self, habit):
        """Тест сериализатора обновления"""
        data = {
            'action': 'попить больше воды',
            'place': 'на работе',
            'time': '10:00',
            'duration_to_complete': 40
        }
        serializer = HabitUpdateSerializer(habit, data=data)
        assert serializer.is_valid(), serializer.errors
        updated_habit = serializer.save()
        assert updated_habit.action == 'попить больше воды'
        assert updated_habit.place == 'на работе'


class TestUserSerializers:
    """Тесты сериализаторов пользователей"""

    @pytest.mark.django_db
    def test_register_serializer_valid(self):
        """Тест сериализатора регистрации с валидными данными"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('testpass123')

    @pytest.mark.django_db
    def test_register_serializer_passwords_not_match(self):
        """Тест: пароли должны совпадать"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'Пароли не совпадают' in str(serializer.errors['password'])

    @pytest.mark.django_db
    def test_register_serializer_missing_fields(self):
        """Тест: обязательные поля"""
        data = {
            'username': 'newuser'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
        assert 'password' in serializer.errors
