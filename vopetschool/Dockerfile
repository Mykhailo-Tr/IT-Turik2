FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Встановлення системних локалей
RUN apt-get update && \
    apt-get install -y locales && \
    locale-gen uk_UA.UTF-8 en_US.UTF-8 && \
    update-locale LANG=uk_UA.UTF-8

ENV LANG=uk_UA.UTF-8
ENV LANGUAGE=uk_UA:en_US
ENV LC_ALL=uk_UA.UTF-8

# Робоча директорія
WORKDIR /app

# Встановлення залежностей
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копіювання проєкту
COPY . .

# Збір статики та перекладів
RUN python manage.py collectstatic --noinput && \
    python manage.py compilemessages

# Daphne старт
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "vopetschool.asgi:application"]
