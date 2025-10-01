# Используем официальный Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Запуск бота
CMD ["python", "-m", "bot.main"]
