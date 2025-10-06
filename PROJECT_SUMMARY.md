# Mini Chat Backend - Финальная версия

## ✅ Реализованные функции

### 🔐 Аутентификация и авторизация
- ✅ **Регистрация пользователей** с username и password
- ✅ **JWT аутентификация** с access и refresh токенами  
- ✅ **Автоматическое создание профиля** при регистрации
- ✅ **Зашифрованное хранение паролей** (Django встроенное хеширование)
- ✅ **Защита всех API endpoints** JWT токенами

### 👤 Управление профилем
- ✅ **Профиль пользователя** с аватаром по умолчанию
- ✅ **Онлайн статус** (online/offline)
- ✅ **Время последнего входа** с автоматическим обновлением
- ✅ **Редактирование профиля** (имя, email, аватар)
- ✅ **Смена пароля** с валидацией

### 🔍 Поиск пользователей
- ✅ **Поиск по имени пользователя** (username, first_name, last_name)
- ✅ **Список всех пользователей** для выбора собеседника
- ✅ **Отображение статуса онлайн** для каждого пользователя

### 💬 Чат функциональность

#### Чаты 1-на-1:
- ✅ **Создание прямых чатов** между двумя пользователями
- ✅ **Проверка дубликатов** - если чат существует, второй не создается
- ✅ **Тип чата** - direct (1-на-1) или group (для будущего расширения)

#### Сообщения:
- ✅ **Отправка/получение сообщений** через REST API
- ✅ **Сохранение в базу данных** через Django ORM
- ✅ **История сообщений** при открытии чата
- ✅ **Хронологический порядок** сообщений

#### Статусы сообщений:
- ✅ **is_read = false** для новых сообщений
- ✅ **is_read = true** при прочтении получателем
- ✅ **Автоматическая отметка как прочитанных** при открытии чата
- ✅ **Счетчик непрочитанных сообщений** для каждого чата

#### Онлайн статус:
- ✅ **Обновление при входе/выходе** из системы
- ✅ **Отображение статуса** для всех пользователей
- ✅ **Время последнего визита** с автоматическим обновлением

## 🚀 Запуск сервера

```bash
# Активация виртуального окружения
source venv/bin/activate

# Запуск сервера
python manage.py runserver 8001
```

**Сервер доступен по адресу**: `http://127.0.0.1:8001/`

## 📋 API Endpoints

### Аутентификация (`/api/auth/`)
| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register/` | Регистрация пользователя |
| POST | `/api/auth/login/` | Вход в систему |
| POST | `/api/auth/logout/` | Выход из системы |
| POST | `/api/auth/token/refresh/` | Обновление JWT токена |
| GET | `/api/auth/me/` | Текущий пользователь |
| GET/PUT | `/api/auth/profile/` | Просмотр/редактирование профиля |
| POST | `/api/auth/change-password/` | Смена пароля |
| GET | `/api/auth/search/?q=username` | Поиск пользователей |
| GET | `/api/auth/users/` | Список всех пользователей |

### Чат (`/api/chat/`)
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET/POST | `/api/chat/rooms/` | Список/создание комнат чата |
| GET/PUT/DELETE | `/api/chat/rooms/{id}/` | Управление конкретной комнатой |
| GET | `/api/chat/rooms/{id}/history/` | История сообщений комнаты |
| GET | `/api/chat/rooms/{id}/participants/` | Статус участников комнаты |
| GET/POST | `/api/chat/messages/` | Получение/отправка сообщений |
| POST | `/api/chat/create-direct-chat/` | Создание прямого чата |
| GET | `/api/chat/online-users/` | Список онлайн пользователей |

## 🗄️ Модели данных

### User (Django встроенная)
- `username` - Имя пользователя (уникальное)
- `email` - Email адрес  
- `first_name` - Имя
- `last_name` - Фамилия
- `password` - Зашифрованный пароль

### UserProfile
- `user` - Связь с User (OneToOne)
- `is_online` - Статус онлайн (Boolean)
- `last_seen` - Время последнего входа (DateTime)
- `avatar` - URL аватара (по умолчанию placeholder)

### ChatRoom
- `name` - Название комнаты
- `description` - Описание
- `chat_type` - Тип чата (direct/group)
- `created_at` - Дата создания
- `participants` - Участники (ManyToMany с User)

### Message
- `room` - Комната чата (ForeignKey)
- `user` - Отправитель (ForeignKey)
- `content` - Содержание сообщения
- `timestamp` - Время отправки
- `is_read` - Статус прочтения (Boolean)

## 🔒 Безопасность

- ✅ **JWT токены** с автоматической ротацией
- ✅ **Зашифрованные пароли** с встроенным хешированием Django
- ✅ **CORS защита** настроена для frontend
- ✅ **Валидация данных** на уровне сериализаторов
- ✅ **Права доступа** на уровне API views
- ✅ **Проверка принадлежности** к чатам перед доступом

## 📁 Структура проекта

```
Backend/
├── minichat/                    # Настройки Django
│   ├── settings.py             # Конфигурация (JWT, CORS, DRF)
│   ├── urls.py                 # Главные URL маршруты
│   ├── wsgi.py                 # WSGI для production
│   └── asgi.py                 # ASGI для WebSocket (готово)
├── accounts/                    # Управление пользователями
│   ├── models.py               # Сигналы для автосозданий профилей
│   ├── views.py                # JWT аутентификация, поиск
│   ├── serializers.py          # Валидация данных пользователей
│   ├── urls.py                 # Маршруты аутентификации
│   └── admin.py                # Админка для пользователей
├── chat/                       # Чат функциональность
│   ├── models.py               # ChatRoom, Message, UserProfile
│   ├── views.py                # API для чатов и сообщений
│   ├── serializers.py          # Сериализация данных чата
│   ├── urls.py                 # Маршруты чата
│   ├── admin.py                # Админка для чатов
│   ├── consumers.py            # WebSocket consumers (готово)
│   ├── routing.py              # WebSocket маршруты (готово)
│   └── middleware.py           # JWT middleware для WebSocket
├── requirements.txt            # Python зависимости
├── manage.py                   # Django управляющий скрипт
├── db.sqlite3                  # База данных SQLite
├── README.md                   # Документация проекта
├── API_DOCUMENTATION.md        # Детальная API документация
└── WEBSOCKET_DOCUMENTATION.md  # WebSocket документация (готово)
```

## 🎯 Примеры использования

### Регистрация пользователя
```bash
curl -X POST http://127.0.0.1:8001/api/auth/register/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Поиск пользователей
```bash
curl -X GET "http://127.0.0.1:8001/api/auth/search/?q=test" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Создание чата
```bash
curl -X POST http://127.0.0.1:8001/api/chat/create-direct-chat/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"user_id": 2}'
```

### Отправка сообщения
```bash
curl -X POST http://127.0.0.1:8001/api/chat/messages/ \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "room": 1,
    "content": "Привет! Как дела?"
  }'
```

## 🚧 WebSocket (готово к использованию)

WebSocket функциональность полностью реализована и готова к использованию:

- ✅ **Real-time сообщения** через WebSocket
- ✅ **JWT аутентификация** для WebSocket
- ✅ **Автоматическое обновление онлайн статуса**
- ✅ **Индикатор печати**
- ✅ **Уведомления о подключении/отключении**

Для активации WebSocket:
1. Установите Redis
2. Обновите настройки в `settings.py`
3. Добавьте `daphne` и `channels` в `INSTALLED_APPS`

## 💡 Готовность к production

Backend полностью готов для подключения React frontend и может быть легко адаптирован для production с минимальными изменениями:

- ✅ Все основные функции чата реализованы
- ✅ Безопасность настроена
- ✅ API документирован
- ✅ Код структурирован и комментирован
- ✅ Миграции настроены
- ✅ Админка настроена

## 📄 Файлы документации

- `README.md` - Основная документация проекта
- `API_DOCUMENTATION.md` - Детальное описание всех API endpoints
- `WEBSOCKET_DOCUMENTATION.md` - Документация по WebSocket функциональности

## 🎉 Результат

Создан полнофункциональный Django REST API backend для мини-чат приложения с поддержкой:

1. ✅ **JWT аутентификации**
2. ✅ **Поиска пользователей**  
3. ✅ **Прямых чатов 1-на-1**
4. ✅ **Real-time статусов сообщений**
5. ✅ **Онлайн статусов пользователей**
6. ✅ **Истории сообщений**
7. ✅ **WebSocket готовности**

Backend готов к подключению React frontend!