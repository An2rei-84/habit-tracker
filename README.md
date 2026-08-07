# Habit Tracker

Трекер полезных привычек на основе книги «Атомные привычки» Джеймса Клира.

## Описание проекта

Бэкенд-часть SPA веб-приложения для отслеживания полезных привычек с интеграцией Telegram бота для отправки напоминаний.

Проект поддерживает принцип формирования привычки: *я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТО]*, с возможностью вознаграждения за выполнение полезных привычек.

## Технологии

- Django 5.0.8
- Django REST Framework 3.15.2
- Celery 5.4.0
- Redis
- Telegram Bot API
- PostgreSQL / SQLite
- JWT авторизация
- drf-spectacular (документация API)

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.template`:
```bash
cp .env.template .env
```

5. Выполните миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

## Запуск проекта

### Запуск Django сервера:
```bash
python manage.py runserver
```

### Запуск Celery worker:
```bash
python manage.py celery_worker
```

### Запуск Celery beat:
```bash
python manage.py celery_beat
```

### Запуск Telegram бота:
```bash
python manage.py runbot
```

## API документация

После запуска сервера документация доступна по адресу:
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/

## Основные эндпоинты

### Авторизация
- `POST /api/users/register/` - Регистрация
- `POST /api/users/token/` - Получение JWT токена
- `GET /api/users/profile/` - Профиль пользователя

### Привычки
- `GET /api/habits/` - Список привычек текущего пользователя
- `POST /api/habits/` - Создание привычки
- `GET /api/habits/{id}/` - Детальный просмотр
- `PUT/PATCH /api/habits/{id}/` - Редактирование
- `DELETE /api/habits/{id}/` - Удаление
- `GET /api/habits/public/` - Список публичных привычек

## Правила валидации

1. Нельзя указывать и вознаграждение, и связанную привычку одновременно
2. Время выполнения не может превышать 120 секунд
3. В связанные привычки можно добавлять только приятные привычки
4. У приятной привычки не может быть вознаграждения или связанной привычки
5. Периодичность выполнения от 1 до 7 дней

## Telegram бот

Бот отправляет напоминания о привычках каждый день в 9:00.

Команды бота:
- `/start` - Начать работу
- `/link` - Привязать аккаунт
- `/list` - Список привычек на сегодня
- `/help` - Справка

## Запуск тестов

```bash
pytest
```

Для генерации HTML отчёта:
```bash
pytest --cov=. --cov-report=html
```

**Покрытие тестами:** 89%

📊 **HTML отчёт о покрытии:** `htmlcov/index.html` (уже сгенерирован, откройте в браузере)

## Структура проекта

```
habit_tracker/
├── config/          # Настройки Django
├── habits/          # Приложение привычек
├── users/           # Приложение пользователей
├── bot/             # Telegram бот
├── tests/           # Тесты
├── .env             # Переменные окружения (не в git)
└── .env.template    # Шаблон переменных
```

## Лицензия

MIT
