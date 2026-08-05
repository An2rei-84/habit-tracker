"""
Валидаторы для модели Habit
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_reward_and_related_habit(reward, related_habit):
    """
    Исключить одновременный выбор связанной привычки и указания вознаграждения.
    Можно заполнить только одно из двух полей.
    """
    if reward and related_habit:
        raise ValidationError({
            'non_field_errors': _(
                'Нельзя указывать и вознаграждение, и связанную привычку одновременно. '
                'Выберите что-то одно.'
            )
        })


def validate_execution_time(duration_to_complete):
    """
    Время выполнения должно быть не больше 120 секунд.
    """
    if duration_to_complete and duration_to_complete > 120:
        raise ValidationError({
            'duration_to_complete': _(
                'Время на выполнение привычки не может превышать 120 секунд.'
            )
        })


def validate_related_habit_is_pleasant(related_habit):
    """
    В связанные привычки могут попадать только привычки с признаком приятной привычки.
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError({
            'related_habit': _(
                'В связанные привычки можно добавлять только привычки с признаком "Приятная привычка".'
            )
        })


def validate_pleasant_habit_restrictions(is_pleasant, reward, related_habit):
    """
    У приятной привычки не может быть вознаграждения или связанной привычки.
    """
    if is_pleasant and (reward or related_habit):
        raise ValidationError({
            'non_field_errors': _(
                'У приятной привычки не может быть вознаграждения или связанной привычки.'
            )
        })


def validate_periodicity(periodicity):
    """
    Нельзя выполнять привычку реже 1 раза в 7 дней.
    Периодичность должна быть от 1 до 7 дней.
    """
    if periodicity is not None and (periodicity < 1 or periodicity > 7):
        raise ValidationError({
            'periodicity': _(
                'Периодичность выполнения привычки должна быть от 1 до 7 дней.'
            )
        })
