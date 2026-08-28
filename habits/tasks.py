"""
Celery задачи для отправки напоминаний о привычках
"""

from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from bot.services import TelegramBotService


@shared_task
def send_habit_reminders():
    """
    Отправка напоминаний о привычках в Telegram

    Запускается каждую минуту
    Отправляет уведомления пользователям о привычках, которые нужно выполнить сегодня
    Учитывает время выполнения привычки
    """
    today = timezone.now().date()
    current_time = timezone.now().time()

    # Находим привычки, которые нужно выполнить сегодня
    habits_to_remind = Habit.objects.filter(is_pleasant=False, user__telegram_chat_id__isnull=False)

    sent_count = 0
    failed_count = 0

    for habit in habits_to_remind:
        # Проверяем, нужно ли отправлять уведомление сегодня
        if should_send_reminder_today(habit, today):
            # Проверяем, совпадает ли текущее время с временем привычки (с точностью до минуты)
            if should_send_reminder_now(habit, current_time):
                try:
                    # Формируем сообщение
                    message = format_habit_reminder(habit)

                    # Отправляем в Telegram
                    bot_service = TelegramBotService()
                    bot_service.send_message(chat_id=habit.user.telegram_chat_id, text=message)
                    sent_count += 1
                except Exception as e:
                    print(f"Ошибка отправки уведомления пользователю {habit.user.username}: {e}")
                    failed_count += 1

    print(f"Отправлено уведомлений: {sent_count}, Ошибок: {failed_count}")
    return {"sent": sent_count, "failed": failed_count}


def should_send_reminder_now(habit, current_time):
    """
    Определяет, нужно ли отправить уведомление сейчас

    Сравнивает текущее время с временем привычки (с точностью до минуты)
    """
    return habit.time.hour == current_time.hour and habit.time.minute == current_time.minute


def should_send_reminder_today(habit, today):
    """
    Определяет, нужно ли отправлять уведомление сегодня

    Учитывает периодичность выполнения привычки
    """
    # Если привычка создана сегодня, отправляем уведомление
    if habit.created_at.date() == today:
        return True

    # Вычисляем разницу в днях с момента создания
    days_since_creation = (today - habit.created_at.date()).days

    # Если дней прошло кратно периоду, отправляем уведомление
    return days_since_creation % habit.periodicity == 0


def format_habit_reminder(habit):
    """
    Форматирует сообщение о привычке для отправки в Telegram
    """
    message = "⏰ Напоминание о привычке!\n\n"
    message += f"📌 {habit.action}\n"
    message += f"📍 Место: {habit.place}\n"
    message += f"⏰ Время: {habit.time}\n"
    message += f"⏱️ Время на выполнение: {habit.duration_to_complete} сек\n"

    if habit.reward:
        message += f"🎁 Вознаграждение: {habit.reward}\n"
    elif habit.related_habit:
        message += f"🎁 Вознаграждение: {habit.related_habit.action}\n"

    message += "\n💪 Не забудь выполнить! Ты можешь это! 💪"

    return message
