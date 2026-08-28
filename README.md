# Habit Tracker

![CI/CD](https://github.com/An2rei-84/habit-tracker/actions/workflows/ci-cd.yml/badge.svg?branch=develop)

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
- Docker & Docker Compose
- Nginx

## Содержание

- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск (Docker)](#локальный-запуск-docker)
  - [Локальный запуск (виртуальное окружение)](#локальный-запуск-виртуальное-окружение)
- [API документация](#api-документация)
- [Основные эндпоинты](#основные-эндпоинты)
- [Правила валидации](#правила-валидации)
- [Telegram бот](#telegram-бот)
- [CI/CD и Деплой](#cicd-и-деплой)
- [Запуск тестов](#запуск-тестов)

---

## Установка и запуск

### Локальный запуск (Docker)

**Требуемые компоненты:**
- Docker
- Docker Compose

**Шаги:**

1. Клонируйте репозиторий:
```bash
git clone https://github.com/An2rei-84/habit-tracker.git
cd habit-tracker
```

2. Создайте файл `.env` на основе `.env.template`:
```bash
cp .env.template .env
```

3. Отредактируйте `.env` файл (минимальные настройки для Docker):
```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=habit_tracker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

TELEGRAM_BOT_TOKEN=your-telegram-bot-token

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

4. Запустите все сервисы одной командой:
```bash
docker compose up --build
```

5. Выполните миграции и создайте суперпользователя (в отдельном терминале):
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

6. Доступ к сервисам:
- **API**: http://localhost/api/docs/
- **Admin**: http://localhost/admin/
- **API Schema**: http://localhost/api/schema/

**Остановка:**
```bash
docker compose down
```

**Остановка с удалением volumes:**
```bash
docker compose down -v
```

### Локальный запуск (виртуальное окружение)

**Требуемые компоненты:**
- Python 3.13+
- Redis
- PostgreSQL (опционально)

**Шаги:**

1. Клонируйте репозиторий

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.template`

5. Выполните миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запуск Django сервера:
```bash
python manage.py runserver
```

8. Запуск Celery worker (в отдельном терминале):
```bash
python manage.py celery_worker
```

9. Запуск Celery beat (в отдельном терминале):
```bash
python manage.py celery_beat
```

10. Запуск Telegram бота (в отдельном терминале):
```bash
python manage.py runbot
```

---

## API документация

После запуска сервера документация доступна по адресу:
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/

---

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

---

## Правила валидации

1. Нельзя указывать и вознаграждение, и связанную привычку одновременно
2. Время выполнения не может превышать 120 секунд
3. В связанные привычки можно добавлять только приятные привычки
4. У приятной привычки не может быть вознаграждения или связанной привычки
5. Периодичность выполнения от 1 до 7 дней

---

## Telegram бот

Бот отправляет напоминания о привычках каждый день в 9:00.

Команды бота:
- `/start` - Начать работу
- `/link` - Привязать аккаунт
- `/list` - Список привычек на сегодня
- `/help` - Справка

---

## CI/CD и Деплой

### Структура CI/CD пайплайна

GitHub Actions автоматически выполняет:
1. **Тесты**: pytest с coverage отчетом
2. **Линтинг**: black и ruff
3. **Сборка**: Docker образ
4. **Деплой**: на сервер при пуше в ветку `develop`

### Требуемые GitHub Secrets

Для деплоя на свой сервер настройте следующие Secrets в репозитории:

| Secret | Значение | Описание |
|--------|----------|----------|
| `SSH_PRIVATE_KEY` | Ваш приватный ключ | Приватный SSH ключ для доступа к серверу |
| `SSH_HOST` | IP или домен | Адрес вашего сервера |
| `SSH_USER` | Пользователь | Пользователь SSH (рекомендуется не root) |
| `SECRET_KEY` | Сгенерировать | Django SECRET_KEY для production |
| `DB_PASSWORD` | Придумать | Пароль PostgreSQL (рекомендуется сложный) |
| `TELEGRAM_BOT_TOKEN` | Ваш токен | Токен Telegram бота от @BotFather |
| `ALLOWED_HOSTS` | IP или домен | Например: `your-domain.com` |
| `CORS_ALLOWED_ORIGINS` | Фронтенд URL | Например: `https://yourdomain.com` |

### Требования к серверу

Любой VPS (Ubuntu 20.04+ / Debian 11+):
- Не менее 2GB RAM
- 20GB свободного дискового пространства
- Установленные Docker и Docker Compose
- SSH-доступ по ключу

**Открытые порты:**
- 80 (HTTP)
- 443 (HTTPS)
- 22 (SSH)

> **Безопасность:** запретите парольный вход SSH (`PasswordAuthentication no` в `/etc/ssh/sshd_config`), не деплойте под root и настройте fail2ban.

### Процесс деплоя

1. **Добавьте Secrets в GitHub репозиторий:**
   - Перейдите в Settings → Secrets and variables → Actions
   - Добавьте все секреты из таблицы выше

2. **Пуш в ветку `develop` запускает автоматический деплой:**
```bash
git checkout develop
git merge feature
git push origin develop
```

### Структура на сервере

После деплоя структура на сервере:
```
~/habit-tracker/
├── docker-compose.yml
├── .env
└── (все необходимые volumes: postgres_data, static_volume, media_volume)
```

---

## Запуск тестов

```bash
pytest
```

Для генерации HTML отчёта:
```bash
pytest --cov=. --cov-report=html
```

**Покрытие тестами:** 90%

📊 **HTML отчёт о покрытии:** `htmlcov/index.html` (генерируется при запуске `pytest`)

---

## Структура проекта

```
habit_tracker/
├── config/          # Настройки Django
├── habits/          # Приложение привычек
├── users/           # Приложение пользователей
├── bot/             # Telegram бот
├── tests/           # Тесты
├── nginx/           # Nginx конфигурация
├── .github/         # GitHub Actions workflows
├── Dockerfile       # Docker образ
├── docker-compose.yml # Docker Compose конфигурация
├── requirements.txt # Все зависимости
└── requirements-prod.txt # Production зависимости
```

---

## Лицензия

MIT
