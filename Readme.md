# Habit Tracker - Backend

Система для отслеживания привычек с интеграцией Telegram бота.

## Содержание

- [Технологии](#технологии)
- [Локальный запуск](#локальный-запуск)
- [Запуск с Docker](#запуск-с-docker)
- [CI/CD](#cicd)
- [Деплой на сервер](#деплой-на-сервер)
- [API Документация](#api-документация)
- [Тестирование](#тестирование)

##  Технологии

- Python 3.10
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 14
- Redis 7
- Celery 5.3
- Nginx
- Docker & Docker Compose
- GitHub Actions (CI/CD)

##  Локальный запуск

### Требования
- Python 3.10+
- Poetry
- PostgreSQL 14+
- Redis 7+

### Установка

1. Клонировать репозиторий:

git clone https://github.com/your-username/habit-tracker.git
cd habit-tracker
2.	Установить зависимости:

poetry install
3.	Создать файл .env из .env.template:

cp .env.template .env
# Отредактируйте .env под свои настройки
4.	Применить миграции:

poetry run python manage.py migrate
5.	Создать суперпользователя:

poetry run python manage.py createsuperuser
6.	Запустить сервер разработки:

poetry run python manage.py runserver
