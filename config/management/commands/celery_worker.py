"""
Management команда для запуска Celery worker
"""

from django.core.management.base import BaseCommand
from celery import current_app


class Command(BaseCommand):
    help = "Запускает Celery worker"

    def add_arguments(self, parser):
        parser.add_argument("--loglevel", type=str, default="info", help="Уровень логирования")

    def handle(self, *args, **options):
        loglevel = options.get("loglevel", "info")

        self.stdout.write(f"Запуск Celery worker с уровнем логирования: {loglevel}")

        # Запускаем worker
        worker = current_app.Worker(
            loglevel=loglevel,
        )

        try:
            worker.start()
        except KeyboardInterrupt:
            self.stdout.write("\nWorker остановлен")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
