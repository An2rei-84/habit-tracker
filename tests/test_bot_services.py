"""
Тесты для Telegram Bot сервисов
"""

from unittest.mock import patch, MagicMock
import pytest

from bot.services import TelegramBotService


class TestTelegramBotService:
    """Тесты для TelegramBotService"""

    def test_get_bot_token(self, settings):
        """Тест получения токена бота"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"
        token = TelegramBotService._get_bot_token()
        assert token == "test_token_123"

    def test_get_bot_token_missing(self, settings):
        """Тест: токен не настроен"""
        settings.TELEGRAM_BOT_TOKEN = ""
        with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
            TelegramBotService._get_bot_token()

    def test_get_base_url(self, settings):
        """Тест получения базового URL"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"
        base_url = TelegramBotService.get_base_url()
        assert "test_token_123" in base_url
        assert "api.telegram.org" in base_url

    @patch("bot.services.httpx.post")
    def test_send_message_success(self, mock_post, settings):
        """Тест успешной отправки сообщения"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        # Мокаем успешный ответ
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = TelegramBotService.send_message(chat_id="123456", text="Test message")

        assert result is True
        mock_post.assert_called_once()

    @patch("bot.services.httpx.post")
    def test_send_message_failure(self, mock_post, settings):
        """Тест неудачной отправки сообщения"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        # Мокаем неуспешный ответ
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": False, "description": "Error"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = TelegramBotService.send_message(chat_id="123456", text="Test message")

        assert result is False

    @patch("bot.services.httpx.post")
    def test_send_message_http_error(self, mock_post, settings):
        """Тест ошибки HTTP"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        # Мокаем HTTP ошибку
        import httpx

        mock_post.side_effect = httpx.HTTPError("Network error")

        result = TelegramBotService.send_message(chat_id="123456", text="Test message")

        assert result is False

    @patch("bot.services.httpx.get")
    def test_get_me_success(self, mock_get, settings):
        """Тест успешного получения информации о боте"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": {"id": 123, "username": "test_bot"}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = TelegramBotService.get_me()

        assert result is not None
        assert result["username"] == "test_bot"

    @patch("bot.services.httpx.get")
    def test_get_me_http_error(self, mock_get, settings):
        """Тест сетевой ошибки при получении информации о боте"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        import httpx

        mock_get.side_effect = httpx.HTTPError("Network error")

        result = TelegramBotService.get_me()

        assert result is None

    @patch("bot.services.httpx.post")
    def test_set_webhook_http_error(self, mock_post, settings):
        """Тест сетевой ошибки при установке webhook"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        import httpx

        mock_post.side_effect = httpx.HTTPError("Network error")

        result = TelegramBotService.set_webhook("https://example.com/webhook")

        assert result is False

    @patch("bot.services.httpx.post")
    def test_delete_webhook_http_error(self, mock_post, settings):
        """Тест сетевой ошибки при удалении webhook"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        import httpx

        mock_post.side_effect = httpx.HTTPError("Network error")

        result = TelegramBotService.delete_webhook()

        assert result is False

    @patch("bot.services.httpx.post")
    def test_set_webhook_success(self, mock_post, settings):
        """Тест успешной установки webhook"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = TelegramBotService.set_webhook("https://example.com/webhook")

        assert result is True

    @patch("bot.services.httpx.post")
    def test_delete_webhook_success(self, mock_post, settings):
        """Тест успешного удаления webhook"""
        settings.TELEGRAM_BOT_TOKEN = "test_token_123"

        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = TelegramBotService.delete_webhook()

        assert result is True
