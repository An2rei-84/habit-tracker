"""
Сервис для работы с Telegram Bot API
"""

import logging
from typing import Optional

import httpx

from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    """
    Сервис для отправки сообщений через Telegram Bot API
    """

    BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/"

    @staticmethod
    def _get_bot_token() -> str:
        """
        Получает токен бота из настроек
        """
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN не настроен в settings")
        return token

    @classmethod
    def get_base_url(cls) -> str:
        """
        Возвращает базовый URL для Telegram Bot API
        """
        token = cls._get_bot_token()
        return f"https://api.telegram.org/bot{token}/"

    @classmethod
    def send_message(
        cls, chat_id: str, text: str, parse_mode: str = "HTML", disable_web_page_preview: bool = True
    ) -> bool:
        """
        Отправляет сообщение в чат Telegram

        Args:
            chat_id: ID чата или username
            text: Текст сообщения
            parse_mode: Режим форматирования (HTML или Markdown)
            disable_web_page_preview: Отключить предпросмотр ссылок

        Returns:
            bool: True если сообщение отправлено успешно
        """
        url = f"{cls.get_base_url()}sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        try:
            response = httpx.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info(f"Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"Ошибка отправки сообщения: {result}")
                return False

        except httpx.HTTPError as e:
            logger.error(f"Ошибка HTTP запроса: {e}")
            return False

    @classmethod
    def get_me(cls) -> Optional[dict]:
        """
        Получает информацию о боте

        Returns:
            dict с информацией о боте или None
        """
        url = f"{cls.get_base_url()}getMe"

        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                return result.get("result")
            return None

        except httpx.HTTPError as e:
            logger.error(f"Ошибка получения информации о боте: {e}")
            return None

    @classmethod
    def set_webhook(cls, webhook_url: str) -> bool:
        """
        Устанавливает webhook для бота

        Args:
            webhook_url: URL webhook

        Returns:
            bool: True если webhook установлен успешно
        """
        url = f"{cls.get_base_url()}setWebhook"

        payload = {"url": webhook_url}

        try:
            response = httpx.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info(f"Webhook установлен: {webhook_url}")
                return True
            return False

        except httpx.HTTPError as e:
            logger.error(f"Ошибка установки webhook: {e}")
            return False

    @classmethod
    def delete_webhook(cls) -> bool:
        """
        Удаляет webhook

        Returns:
            bool: True если webhook удалён успешно
        """
        url = f"{cls.get_base_url()}deleteWebhook"

        try:
            response = httpx.post(url, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info("Webhook удалён")
                return True
            return False

        except httpx.HTTPError as e:
            logger.error(f"Ошибка удаления webhook: {e}")
            return False
