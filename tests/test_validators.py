"""
Тесты для валидаторов
"""
import pytest
from django.core.exceptions import ValidationError

from habits.validators.habit_validators import (
    validate_execution_time,
    validate_periodicity,
    validate_pleasant_habit_restrictions,
    validate_related_habit_is_pleasant,
    validate_reward_and_related_habit,
)


class TestHabitValidators:
    """Тесты валидаторов привычек"""

    def test_validate_reward_and_related_habit_both_set(self):
        """Тест: ошибка когда и reward, и related_habit указаны"""
        with pytest.raises(ValidationError):
            validate_reward_and_related_habit(
                reward='шоколадка',
                related_habit='some_habit'
            )

    def test_validate_reward_and_related_habit_only_reward(self):
        """Тест: ошибка не возникает когда только reward указан"""
        # Не должно вызывать исключение
        validate_reward_and_related_habit(reward='шоколадка', related_habit=None)

    def test_validate_reward_and_related_habit_only_related(self):
        """Тест: ошибка не возникает когда только related_habit указан"""
        # Не должно вызывать исключение
        validate_reward_and_related_habit(reward=None, related_habit='some_habit')

    def test_validate_execution_time_exceeds_120(self):
        """Тест: ошибка когда время больше 120 секунд"""
        with pytest.raises(ValidationError):
            validate_execution_time(121)

    def test_validate_execution_time_exactly_120(self):
        """Тест: ошибка не возникает когда время равно 120 секунд"""
        # Не должно вызывать исключение
        validate_execution_time(120)

    def test_validate_execution_time_less_than_120(self):
        """Тест: ошибка не возникает когда время меньше 120 секунд"""
        # Не должно вызывать исключение
        validate_execution_time(60)

    def test_validate_periodicity_too_low(self):
        """Тест: ошибка когда периодичность меньше 1"""
        with pytest.raises(ValidationError):
            validate_periodicity(0)

    def test_validate_periodicity_too_high(self):
        """Тест: ошибка когда периодичность больше 7"""
        with pytest.raises(ValidationError):
            validate_periodicity(8)

    def test_validate_periodicity_valid_values(self):
        """Тест: валидные значения периодичности"""
        # Не должны вызывать исключения
        validate_periodicity(1)
        validate_periodicity(7)

    def test_validate_pleasant_habit_with_reward(self):
        """Тест: ошибка когда приятная привычка имеет вознаграждение"""
        with pytest.raises(ValidationError):
            validate_pleasant_habit_restrictions(
                is_pleasant=True,
                reward='шоколадка',
                related_habit=None
            )

    def test_validate_pleasant_habit_with_related(self):
        """Тест: ошибка когда приятная привычка имеет связанную привычку"""
        with pytest.raises(ValidationError):
            validate_pleasant_habit_restrictions(
                is_pleasant=True,
                reward=None,
                related_habit='some_habit'
            )

    def test_validate_pleasant_habit_valid(self):
        """Тест: валидная приятная привычка"""
        # Не должно вызывать исключение
        validate_pleasant_habit_restrictions(
            is_pleasant=True,
            reward=None,
            related_habit=None
        )

    def test_validate_related_habit_not_pleasant(self, db):
        """Тест: ошибка когда связанная привычка не приятная"""
        from habits.models import Habit
        from users.models import User

        user = User.objects.create_user(username='test', password='pass')
        related = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='привычка',
            is_pleasant=False,
            periodicity=1,
            duration_to_complete=30
        )

        with pytest.raises(ValidationError):
            validate_related_habit_is_pleasant(related)

    def test_validate_related_habit_is_pleasant(self, db):
        """Тест: нет ошибки когда связанная привычка приятная"""
        from habits.models import Habit
        from users.models import User

        user = User.objects.create_user(username='test', password='pass')
        related = Habit(
            user=user,
            place='дома',
            time='09:00',
            action='приятная привычка',
            is_pleasant=True,
            periodicity=1,
            duration_to_complete=30
        )

        # Не должно вызывать исключение
        validate_related_habit_is_pleasant(related)
