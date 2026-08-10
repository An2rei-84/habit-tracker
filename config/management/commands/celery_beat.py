"""
Management команда для запуска Celery beat
"""

from django.core.management.base import BaseCommand
from celery import current_app


class Command(BaseCommand):
    help = "Запускает Celery beat scheduler"

    def add_arguments(self, parser):
        parser.add_argument("--loglevel", type=str, default="info", help="Уровень логирования")

    def handle(self, *args, **options):
        loglevel = options.get("loglevel", "info")

        self.stdout.write(f"Запуск Celery beat с уровнем логирования: {loglevel}")

        # Запускаем beat scheduler через celery beat binary
        try:
            from celery.bin.beat import beat

            beat_app = beat(app=current_app)
            beat_app.run(loglevel=loglevel)
        except KeyboardInterrupt:
            self.stdout.write("\nBeat остановлен")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
