FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Установка Poetry и зависимостей
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копирование исходного кода
COPY . .

# Сбор статики
RUN python manage.py collectstatic --noinput

# Создание директорий для логов и медиа
RUN mkdir -p /app/logs /app/media /app/tmp/emails

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]


