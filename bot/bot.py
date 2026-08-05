"""
Telegram Bot для Habit Tracker
"""
import logging
from datetime import datetime, time

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from django.conf import settings
from habits.models import Habit
from users.models import User

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start

    Привязывает chat_id к пользователю
    """
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    message = (
        "👋 Привет! Я бот для отслеживания полезных привычек.\n\n"
        "Доступные команды:\n"
        "/help - Справка\n"
        "/link - Привязать аккаунт (если вы ещё не авторизованы)\n"
        "/list - Список ваших привычек на сегодня\n"
    )

    await update.message.reply_text(message)

    logger.info(f"Команда /start от пользователя {username} (chat_id: {chat_id})")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /help
    """
    message = (
        "📖 <b>Справка</b>\n\n"
        "Я помогаю вам отслеживать полезные привычки.\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/link - Привязать Telegram к аккаунту\n"
        "/list - Список привычек на сегодня\n"
        "/help - Эта справка\n\n"
        "<b>Как работает?</b>\n"
        "1. Зарегистрируйтесь на сайте\n"
        "2. Создайте привычки\n"
        "3. Получайте напоминания здесь!\n\n"
        "❓ Если есть вопросы - напишите администратору."
    )

    await update.message.reply_text(message, parse_mode='HTML')


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /link

    Привязывает chat_id к пользователю по username или email
    """
    chat_id = update.effective_chat.id
    telegram_username = update.effective_user.username

    # Пытаемся найти пользователя по telegram_chat_id
    user = User.objects.filter(telegram_chat_id=str(chat_id)).first()

    if user:
        await update.message.reply_text(
            f"✅ Ваш аккаунт уже привязан: {user.username}"
        )
        return

    # Пытаемся найти пользователя по username
    if telegram_username:
        user = User.objects.filter(username=telegram_username).first()

    if user:
        user.telegram_chat_id = str(chat_id)
        user.save()
        await update.message.reply_text(
            f"✅ Аккаунт успешно привязан: {user.username}\n\n"
            "Теперь вы будете получать напоминания о привычках!"
        )
        logger.info(f"Пользователь {user.username} привязал chat_id: {chat_id}")
    else:
        await update.message.reply_text(
            "❌ Не удалось найти ваш аккаунт.\n\n"
            "Убедитесь, что вы:\n"
            "1. Зарегистрированы на сайте\n"
            "2. Ваш username в Telegram совпадает с username на сайте\n\n"
            "Или свяжитесь с администратором."
        )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /list

    Показывает список привычек на сегодня
    """
    chat_id = str(update.effective_chat.id)

    # Ищем пользователя по chat_id
    user = User.objects.filter(telegram_chat_id=chat_id).first()

    if not user:
        await update.message.reply_text(
            "❌ Ваш аккаунт не привязан.\n\n"
            "Используйте команду /link для привязки."
        )
        return

    # Получаем привычки пользователя
    habits = Habit.objects.filter(user=user, is_pleasant=False)

    if not habits.exists():
        await update.message.reply_text(
            "📋 У вас пока нет привычек.\n\n"
            "Создайте привычки на сайте, чтобы получать напоминания!"
        )
        return

    # Формируем сообщение со списком привычек
    message = f"📋 <b>Ваши привычки ({habits.count()})</b>\n\n"

    for habit in habits:
        message += f"⏰ <b>{habit.time}</b> — {habit.action}\n"
        message += f"📍 {habit.place}\n"
        message += f"⏱️ {habit.duration_to_complete} сек\n"

        if habit.reward:
            message += f"🎁 Награда: {habit.reward}\n"
        elif habit.related_habit:
            message += f"🎁 Награда: {habit.related_habit.action}\n"

        message += "\n"

    await update.message.reply_text(message, parse_mode='HTML')


def run_bot():
    """
    Запускает Telegram бота (для разработки/отладки)
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не настроен")
        return

    # Создаём приложение
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("link", link_command))
    application.add_handler(CommandHandler("list", list_command))

    # Запускаем бота
    logger.info("Запуск Telegram бота...")
    application.run_polling(allowed_updates=["message"])
