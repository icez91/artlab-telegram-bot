#!/bin/bash
set -e

# Проверяем docker
if ! command -v docker &> /dev/null
then
    echo "Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

# Проверяем docker-compose
if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose не установлен. Пожалуйста, установите docker-compose."
    exit 1
fi

# Создаём .env файл если нет
if [ ! -f ".env" ]; then
  echo "BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN" > .env
  echo "API_URL=YOUR_API_URL" >> .env
  echo ".env файл создан. Пожалуйста, внесите в него ваш BOT_TOKEN и адрес api."
  exit 1
fi

# Сборка и запуск контейнера
docker-compose up --build -d

echo "Бот запущен в контейнере 'artlab-bot'. Логи можно смотреть командой:"
echo "docker-compose logs -f telegram-bot"
