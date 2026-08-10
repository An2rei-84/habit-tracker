"""
Management команда для запуска Telegram бота
"""

from django.core.management.base import BaseCommand

from bot.bot import run_bot


class Command(BaseCommand):
    help = "Запускает Telegram бота"

    def handle(self, *args, **options):
        """
        Запускает бота
        """
        self.stdout.write("Запуск Telegram бота...")
        try:
            run_bot()
        except KeyboardInterrupt:
            self.stdout.write("\nБот остановлен")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
