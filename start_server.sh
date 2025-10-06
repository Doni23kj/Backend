#!/bin/bash

# Mini Chat Backend Startup Script
# Автоматически активирует виртуальное окружение и запускает сервер

echo "🚀 Запуск Mini Chat Backend..."

# Переходим в папку проекта
cd "/Users/susolutions/Mini Chat/Backend"

# Проверяем существование виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его командой: python3 -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем установку зависимостей
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django не установлен!"
    echo "Установите зависимости: pip install -r requirements.txt"
    exit 1
fi

# Останавливаем старые процессы на порту 8001
echo "🧹 Освобождение порта 8001..."
pkill -f "python manage.py runserver" 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Запускаем сервер
echo "✅ Запуск Django сервера на http://127.0.0.1:8001/"
echo "📡 WebSocket доступен на ws://127.0.0.1:8001/ws/chat/"
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

python manage.py runserver 8001