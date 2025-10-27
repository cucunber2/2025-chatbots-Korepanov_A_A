# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем системные зависимости, чтобы lxml, aiohttp и pydantic-core собирались без ошибок
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем всё приложение внутрь контейнера
COPY . .

# Задаём переменную окружения, чтобы Python не кешировал .pyc файлы
ENV PYTHONUNBUFFERED=1

# Укажи здесь свой основной файл (например bot.py или main.py)
CMD ["python", "bot.py"]
