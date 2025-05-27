#!/bin/sh

echo "[*] Применяем миграции..."
python /app/backend/manage.py migrate

echo "[*] Запуск скрипта инициализации данных..."
python /app/backend/init_tasks.py

echo "[*] Запуск Gunicorn..."
exec gunicorn todo_api.wsgi:application --bind 0.0.0.0:8000 --workers 3