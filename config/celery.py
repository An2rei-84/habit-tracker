"""
Celery configuration for Django integration
"""

import os

from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("habit_tracker")

# Загружаем настройки из Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически обнаруживаем задачи в установленных приложениях
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Тестовая задача для проверки работы Celery"""
    print(f"Request: {self.request!r}")
