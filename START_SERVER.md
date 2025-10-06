# 🚀 Как запустить Mini Chat Backend

## ⚠️ ВАЖНО: Всегда используйте виртуальное окружение!

### 🎯 САМЫЙ ПРОСТОЙ СПОСОБ:

```bash
# Запуск одной командой через скрипт:
cd "/Users/susolutions/Mini Chat/Backend" && ./start_server.sh
```

### 🔧 Ручной запуск:

```bash
# 1. Переходим в папку проекта
cd "/Users/susolutions/Mini Chat/Backend"

# 2. Активируем виртуальное окружение
source venv/bin/activate

# 3. Запускаем сервер
python manage.py runserver 8001
```

### ❌ ТИПИЧНЫЕ ОШИБКИ:

```bash
# НЕ используйте эти команды:
python manage.py runserver           # ❌ "zsh: command not found: python"
python3 manage.py runserver          # ❌ "ModuleNotFoundError: No module named 'daphne'"
./manage.py runserver                # ❌ Без виртуального окружения
```

### 💡 ПОЧЕМУ ВОЗНИКАЕТ ОШИБКА "command not found: python"?

Когда виртуальное окружение **НЕ активировано**:
- Команда `python` не существует в системе
- Доступен только `python3` 
- Но в `python3` нет установленных Django пакетов

Когда виртуальное окружение **активировано** (`source venv/bin/activate`):
- Команда `python` указывает на `/Users/susolutions/Mini Chat/Backend/venv/bin/python`
- Все пакеты (Django, DRF, Channels) доступны

### 🔍 Проверка статуса:

После запуска вы должны увидеть:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Django version 5.2.7, using settings 'minichat.settings'
Starting ASGI/Daphne version 4.0.0 development server at http://127.0.0.1:8001/
Quit the server with CONTROL-C.
```

### 🌐 Доступ к сервису:

- **API Server:** http://127.0.0.1:8001/
- **Admin Panel:** http://127.0.0.1:8001/admin/
- **WebSocket:** ws://127.0.0.1:8001/ws/chat/{room_id}/

### 🛠️ Если порт 8001 занят:

```bash
# Останавливаем все процессы Django
pkill -f "python manage.py runserver"

# Или принудительно освобождаем порт
lsof -ti:8001 | xargs kill -9

# Затем запускаем заново
source venv/bin/activate && python manage.py runserver 8001
```

### 📋 Быстрая команда (одной строкой):

```bash
cd "/Users/susolutions/Mini Chat/Backend" && source venv/bin/activate && python manage.py runserver 8001
```

---

## 🎯 Backend полностью готов!

✅ Все API endpoints работают  
✅ WebSocket real-time messaging  
✅ JWT аутентификация  
✅ SQLite база данных  
✅ Django Admin панель  

**Готов к подключению React frontend!** 🚀