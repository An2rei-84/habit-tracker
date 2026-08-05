"""
Модель привычки для Habit Tracker
"""
from django.core.exceptions import ValidationError
from django.db import models

from users.models import User

from habits.validators.habit_validators import (
    validate_execution_time,
    validate_periodicity,
    validate_pleasant_habit_restrictions,
    validate_related_habit_is_pleasant,
    validate_reward_and_related_habit,
)


class Habit(models.Model):
    """
    Модель привычки

    Основная сущность для отслеживания полезных привычек.
    Основана на книге «Атомные привычки» Джеймса Клира.

    Правило формирования привычки:
    я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТО]

    За каждую полезную привычку необходимо себя вознаграждать
    или сразу после делать приятную привычку.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь',
        help_text='Создатель привычки'
    )
    place = models.CharField(
        max_length=100,
        verbose_name='Место',
        help_text='Место, в котором необходимо выполнять привычку'
    )
    time = models.TimeField(
        verbose_name='Время',
        help_text='Время, когда необходимо выполнять привычку'
    )
    action = models.CharField(
        max_length=255,
        verbose_name='Действие',
        help_text='Действие, которое представляет собой привычку'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка',
        help_text='Признак приятной привычки (способ вознаграждения)'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_to',
        verbose_name='Связанная привычка',
        help_text='Приятная привычка, которая связана с полезной'
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Периодичность (дни)',
        help_text='Периодичность выполнения привычки в днях (от 1 до 7)'
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение',
        help_text='Чем пользователь должен себя вознаградить после выполнения'
    )
    duration_to_complete = models.PositiveSmallIntegerField(
        verbose_name='Время на выполнение (секунды)',
        help_text='Время, которое предположительно потратит пользователь (макс. 120 сек)'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичная привычка',
        help_text='Признак публичности (другие пользователи могут видеть)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(duration_to_complete__lte=120),
                name='duration_to_complete_not_exceed_120'
            ),
            models.CheckConstraint(
                check=models.Q(periodicity__gte=1) & models.Q(periodicity__lte=7),
                name='periodicity_between_1_and_7'
            ),
        ]

    def __str__(self):
        return f'Я буду {self.action} в {self.time} в {self.place}'

    def clean(self):
        """
        Дополнительная валидация модели.
        Выполняет проверки, которые требуют отношения между полями.
        """
        super().clean()

        # Проверка: нельзя указывать и вознаграждение, и связанную привычку
        validate_reward_and_related_habit(self.reward, self.related_habit)

        # Проверка: время выполнения не больше 120 секунд
        validate_execution_time(self.duration_to_complete)

        # Проверка: связанная привычка должна быть приятной
        if self.related_habit:
            validate_related_habit_is_pleasant(self.related_habit)

        # Проверка: у приятной привычки не может быть вознаграждения или связанной привычки
        validate_pleasant_habit_restrictions(
            self.is_pleasant,
            self.reward,
            self.related_habit
        )

        # Проверка: периодичность от 1 до 7 дней
        validate_periodicity(self.periodicity)

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для вызова clean().
        """
        self.full_clean()
        super().save(*args, **kwargs)
