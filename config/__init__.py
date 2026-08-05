"""
Celery application initialization for Django
"""
# Это обеспечит интеграцию Celery с Django при старте приложения
from .celery import app as celery_app

__all__ = ('celery_app',)
