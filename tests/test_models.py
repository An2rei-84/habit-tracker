"""
Тесты для моделей
"""
import pytest
from django.core.exceptions import ValidationError

from habits.models import Habit
from users.models import User


class TestHabitModel:
    """Тесты модели Habit"""

    def test_create_habit(self, user):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )
        assert habit.user == user
        assert habit.place == 'дома'
        assert habit.action == 'попить воды'
        assert habit.periodicity == 1
        assert habit.duration_to_complete == 30

    def test_habit_str(self, habit):
        """Тест строкового представления привычки"""
        str_habit = str(habit)
        assert 'попить воды' in str_habit
        assert str(habit.time) in str_habit

    def test_reward_and_related_habit_mutually_exclusive(self, user, pleasant_habit):
        """Тест: нельзя указывать и вознаграждение, и связанную привычку"""
        habit = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30,
            reward='шоколадка',
            related_habit=pleasant_habit
        )
        with pytest.raises(ValidationError) as exc_info:
            habit.full_clean()
        assert 'нельзя указывать и вознаграждение' in str(exc_info.value).lower()

    def test_execution_time_max_120_seconds(self, user):
        """Тест: время выполнения не может превышать 120 секунд"""
        habit = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='читать книгу',
            periodicity=1,
            duration_to_complete=121
        )
        with pytest.raises(ValidationError) as exc_info:
            habit.full_clean()
        assert '120' in str(exc_info.value)

    def test_related_habit_must_be_pleasant(self, user):
        """Тест: связанная привычка должна быть приятной"""
        # Создаём полезную привычку без вознаграждения
        useful_habit = Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        # Создаём НЕ приятную привычку для проверки валидации
        non_pleasant_habit = Habit(
            user=user,
            place='дома',
            time='09:05',
            action='посмотреть сериал',
            is_pleasant=False,
            periodicity=1,
            duration_to_complete=60
        )
        non_pleasant_habit.save()

        useful_habit.related_habit = non_pleasant_habit
        with pytest.raises(ValidationError) as exc_info:
            useful_habit.full_clean()
        assert 'приятн' in str(exc_info.value).lower()

    def test_pleasant_habit_no_reward_or_related(self, user):
        """Тест: у приятной привычки не может быть вознаграждения или связанной привычки"""
        habit = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='посмотреть сериал',
            is_pleasant=True,
            periodicity=1,
            duration_to_complete=60,
            reward='шоколадка'
        )
        with pytest.raises(ValidationError) as exc_info:
            habit.full_clean()
        assert 'приятной привычки' in str(exc_info.value).lower()

    def test_periodicity_between_1_and_7(self, user):
        """Тест: периодичность от 1 до 7 дней"""
        habit = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=8,
            duration_to_complete=30
        )
        with pytest.raises(ValidationError) as exc_info:
            habit.full_clean()
        assert '7' in str(exc_info.value)

    def test_periodicity_cannot_be_zero(self, user):
        """Тест: периодичность не может быть 0"""
        habit = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=0,
            duration_to_complete=30
        )
        with pytest.raises(ValidationError):
            habit.full_clean()

    def test_pleasant_habit_with_related_habit(self, user):
        """Тест: приятная привычка не может иметь связанную привычку"""
        pleasant_habit1 = Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='посмотреть сериал',
            is_pleasant=True,
            periodicity=1,
            duration_to_complete=60
        )

        pleasant_habit2 = Habit(
            user=user,
            place='дома',
            time='10:00',
            action='почитать',
            is_pleasant=True,
            periodicity=1,
            duration_to_complete=30,
            related_habit=pleasant_habit1
        )
        with pytest.raises(ValidationError):
            pleasant_habit2.full_clean()


class TestUserModel:
    """Тесты модели User"""

    def test_create_user(self, db):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')

    def test_user_str(self, user):
        """Тест строкового представления пользователя"""
        assert str(user) == user.username

    def test_user_telegram_chat_id(self, user):
        """Тест поля telegram_chat_id"""
        user.telegram_chat_id = '123456789'
        user.save()
        assert user.telegram_chat_id == '123456789'
