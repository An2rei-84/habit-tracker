"""
Сериализаторы для модели Habit
"""

from rest_framework import serializers

from habits.models import Habit
from habits.validators.habit_validators import (
    validate_execution_time,
    validate_periodicity,
    validate_pleasant_habit_restrictions,
    validate_related_habit_is_pleasant,
    validate_reward_and_related_habit,
)


class HabitListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка привычек (минимальные поля)
    """

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "action",
            "place",
            "time",
            "is_pleasant",
            "periodicity",
            "duration_to_complete",
            "is_public",
            "username",
            "created_at",
        ]


class HabitDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра привычки
    """

    username = serializers.CharField(source="user.username", read_only=True)
    related_habit_action = serializers.CharField(source="related_habit.action", read_only=True, allow_null=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "username",
            "action",
            "place",
            "time",
            "is_pleasant",
            "related_habit",
            "related_habit_action",
            "periodicity",
            "reward",
            "duration_to_complete",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


class HabitCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания привычки с валидацией
    """

    class Meta:
        model = Habit
        fields = [
            "action",
            "place",
            "time",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration_to_complete",
            "is_public",
        ]

    def validate(self, data):
        """
        Дополнительная валидация на уровне сериализатора
        """
        related_habit = data.get("related_habit")
        reward = data.get("reward")
        is_pleasant = data.get("is_pleasant", False)
        duration_to_complete = data.get("duration_to_complete")
        periodicity = data.get("periodicity", 1)

        # Проверка: нельзя указывать и вознаграждение, и связанную привычку
        validate_reward_and_related_habit(reward, related_habit)

        # Проверка: время выполнения не больше 120 секунд
        if duration_to_complete:
            validate_execution_time(duration_to_complete)

        # Проверка: связанная привычка должна быть приятной
        if related_habit:
            # Если объект передан через ID, получаем его из БД для проверки
            if isinstance(related_habit, int):
                try:
                    habit_obj = Habit.objects.get(id=related_habit)
                    validate_related_habit_is_pleasant(habit_obj)
                except Habit.DoesNotExist:
                    raise serializers.ValidationError({"related_habit": "Указанная связанная привычка не существует."})
            else:
                validate_related_habit_is_pleasant(related_habit)

        # Проверка: у приятной привычки не может быть вознаграждения или связанной привычки
        validate_pleasant_habit_restrictions(is_pleasant, reward, related_habit)

        # Проверка: периодичность от 1 до 7 дней
        validate_periodicity(periodicity)

        return data


class HabitUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для редактирования привычки
    """

    class Meta:
        model = Habit
        fields = [
            "action",
            "place",
            "time",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration_to_complete",
            "is_public",
        ]

    def validate(self, data):
        """
        Дополнительная валидация при обновлении
        """
        instance = self.instance

        # Получаем значения из data или из instance, если они не были переданы
        related_habit = data.get("related_habit", instance.related_habit if instance else None)
        reward = data.get("reward", instance.reward if instance else None)
        is_pleasant = data.get("is_pleasant", instance.is_pleasant if instance else False)
        duration_to_complete = data.get("duration_to_complete", instance.duration_to_complete if instance else None)
        periodicity = data.get("periodicity", instance.periodicity if instance else 1)

        # Проверка: нельзя указывать и вознаграждение, и связанную привычку
        validate_reward_and_related_habit(reward, related_habit)

        # Проверка: время выполнения не больше 120 секунд
        if duration_to_complete:
            validate_execution_time(duration_to_complete)

        # Проверка: связанная привычка должна быть приятной
        if related_habit:
            if isinstance(related_habit, int):
                try:
                    habit_obj = Habit.objects.get(id=related_habit)
                    validate_related_habit_is_pleasant(habit_obj)
                except Habit.DoesNotExist:
                    raise serializers.ValidationError({"related_habit": "Указанная связанная привычка не существует."})
            else:
                validate_related_habit_is_pleasant(related_habit)

        # Проверка: у приятной привычки не может быть вознаграждения или связанной привычки
        validate_pleasant_habit_restrictions(is_pleasant, reward, related_habit)

        # Проверка: периодичность от 1 до 7 дней
        validate_periodicity(periodicity)

        return data
