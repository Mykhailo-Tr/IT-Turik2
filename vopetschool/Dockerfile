# Базовий Python-образ
FROM python:3.10-slim

# Системні змінні
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Встановлення Python-залежностей
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копіюємо увесь код проєкту
COPY . .

# Команда за замовчуванням — запуск Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "vopetschool.asgi:application"]
