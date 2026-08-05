"""
Тесты для Celery задач
"""
from unittest.mock import patch, MagicMock
from datetime import time, date

import pytest
from django.utils import timezone

from habits.models import Habit
from habits.tasks import send_habit_reminders, should_send_reminder_today, format_habit_reminder
from users.models import User


class TestCeleryTasks:
    """Тесты Celery задач"""

    @patch('habits.tasks.TelegramBotService')
    def test_send_habit_reminders(self, mock_bot_service, db):
        """Тест отправки напоминаний"""
        # Создаём пользователя с telegram_chat_id
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            telegram_chat_id='123456789'
        )

        # Создаём привычку
        habit = Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        # Мокаем метод send_message
        mock_instance = MagicMock()
        mock_bot_service.return_value = mock_instance
        mock_instance.send_message.return_value = True

        # Вызываем задачу
        result = send_habit_reminders()

        # Проверяем, что send_message был вызван
        assert result['sent'] >= 1

    def test_should_send_reminder_today_created_today(self, user):
        """Тест: отправлять уведомление для только что созданной привычки"""
        habit = Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        result = should_send_reminder_today(habit, timezone.now().date())
        assert result is True

    def test_should_send_reminder_today_periodicity_1(self, user):
        """Тест: ежедневная привычка"""
        habit = Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        # При периодичности 1 день должны отправлять каждый день
        today = timezone.now().date()
        result = should_send_reminder_today(habit, today)
        assert result is True

    def test_should_send_reminder_today_periodicity_7(self, user):
        """Тест: еженедельная привычка"""
        habit = Habit.objects.create(
            user=user,
            place='парк',
            time='07:00',
            action='пробежка',
            periodicity=7,
            duration_to_complete=120
        )

        # При периодичности 7 дней должны отправлять раз в неделю
        today = timezone.now().date()
        days_since_creation = (today - habit.created_at.date()).days

        # Если прошло 0, 7, 14... дней - отправляем
        if days_since_creation % 7 == 0:
            result = should_send_reminder_today(habit, today)
            assert result is True
        else:
            result = should_send_reminder_today(habit, today)
            assert result is False

    def test_format_habit_reminder(self, habit):
        """Тест форматирования напоминания"""
        message = format_habit_reminder(habit)

        assert 'попить воды' in message
        assert 'дома' in message
        assert str(habit.time) in message
        assert str(habit.duration_to_complete) in message
        assert 'Напоминание о привычке' in message

    def test_format_habit_reminder_with_reward(self, habit):
        """Тест форматирования с вознаграждением"""
        message = format_habit_reminder(habit)

        assert 'Вознаграждение' in message or 'Награда' in message
        assert habit.reward in message

    @patch('habits.tasks.TelegramBotService')
    def test_send_reminder_no_telegram_id(self, mock_bot_service, db):
        """Тест: не отправлять пользователям без telegram_chat_id"""
        # Создаём пользователя БЕЗ telegram_chat_id
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='попить воды',
            periodicity=1,
            duration_to_complete=30
        )

        # Мокаем сервис
        mock_instance = MagicMock()
        mock_bot_service.return_value = mock_instance
        mock_instance.send_message.return_value = True

        # Вызываем задачу
        result = send_habit_reminders()

        # Не должно быть отправлено сообщений
        assert result['sent'] == 0
        # send_message не должен быть вызван
        mock_instance.send_message.assert_not_called()

    @patch('habits.tasks.TelegramBotService')
    def test_send_reminder_pleasant_habit_not_sent(self, mock_bot_service, db):
        """Тест: не отправлять напоминания для приятных привычек"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            telegram_chat_id='123456789'
        )

        # Создаём приятную привычку
        Habit.objects.create(
            user=user,
            place='дома',
            time='09:00',
            action='посмотреть сериал',
            is_pleasant=True,
            periodicity=1,
            duration_to_complete=60
        )

        # Мокаем сервис
        mock_instance = MagicMock()
        mock_bot_service.return_value = mock_instance
        mock_instance.send_message.return_value = True

        # Вызываем задачу
        result = send_habit_reminders()

        # Не должно быть отправлено сообщений для приятных привычек
        assert result['sent'] == 0
