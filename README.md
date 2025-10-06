# Mini Chat Backend

Django REST API backend для мини-чат приложения с JWT аутентификацией.

## Функциональность

### 🔹 Основные функции пользователя

- **Регистрация** - username и password, автоматическое создание профиля
- **Авторизация** - JWT токены для защиты API
- **Профиль** - имя пользователя, аватар, онлайн-статус, время последнего входа
- **Поиск пользователей** - поиск по имени для начала чатов
- **Чат** - отправка/получение сообщений, история сообщений
- **Редактирование профиля** - обновление личной информации и аватара

### 🔹 Технический стек

- **Backend**: Django + Django REST Framework
- **Аутентификация**: JWT токены (djangorestframework-simplejwt)
- **База данных**: SQLite (встроенная в Django)
- **CORS**: django-cors-headers для связи с frontend

## Установка и запуск

### 1. Клонирование и настройка

```bash
# Перейти в папку Backend
cd "Mini Chat/Backend"

# Создать виртуальное окружение
python3 -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate  # для macOS/Linux
# или
venv\\Scripts\\activate  # для Windows

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Выполнить миграции
python manage.py migrate

# Создать суперпользователя (опционально)
python manage.py createsuperuser
```

### 3. Запуск сервера

```bash
# Запустить сервер разработки
python manage.py runserver
```

Сервер будет доступен по адресу: `http://127.0.0.1:8000/`

### 4. Доступ к админке Django

После создания суперпользователя можно войти в админку:
`http://127.0.0.1:8000/admin/`

## Структура проекта

```
Backend/
├── minichat/           # Основные настройки Django
│   ├── settings.py     # Конфигурация проекта
│   ├── urls.py         # Главные URL маршруты
│   └── asgi.py         # ASGI конфигурация (для WebSocket)
├── accounts/           # Приложение управления пользователями
│   ├── models.py       # Модели пользователей
│   ├── views.py        # API views для аутентификации
│   ├── serializers.py  # Сериализаторы для API
│   └── urls.py         # URL маршруты для аутентификации
├── chat/               # Приложение чата
│   ├── models.py       # Модели чата (ChatRoom, Message, UserProfile)
│   ├── views.py        # API views для чата
│   ├── serializers.py  # Сериализаторы для чата
│   ├── consumers.py    # WebSocket consumers (для будущего использования)
│   └── urls.py         # URL маршруты для чата
├── requirements.txt    # Python зависимости
├── manage.py          # Django управляющий скрипт
└── db.sqlite3         # База данных SQLite
```

## API Endpoints

### Аутентификация (`/api/auth/`)

- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход в систему
- `POST /api/auth/logout/` - Выход из системы
- `POST /api/auth/token/refresh/` - Обновление JWT токена
- `GET /api/auth/me/` - Получить текущего пользователя
- `GET/PUT /api/auth/profile/` - Просмотр/редактирование профиля
- `POST /api/auth/change-password/` - Смена пароля
- `GET /api/auth/search/?q=username` - Поиск пользователей
- `GET /api/auth/users/` - Список всех пользователей

### Чат (`/api/chat/`)

- `GET/POST /api/chat/rooms/` - Список/создание комнат чата
- `GET/PUT/DELETE /api/chat/rooms/{id}/` - Управление конкретной комнатой
- `GET /api/chat/rooms/{id}/history/` - История сообщений комнаты
- `GET/POST /api/chat/messages/` - Получение/отправка сообщений
- `POST /api/chat/create-direct-chat/` - Создание прямого чата
- `GET /api/chat/online-users/` - Список онлайн пользователей
- `POST /api/chat/rooms/{id}/join/` - Присоединиться к комнате
- `POST /api/chat/rooms/{id}/leave/` - Покинуть комнату

## Модели данных

### User (Django встроенная модель)
- `username` - Имя пользователя
- `email` - Email адрес
- `first_name` - Имя
- `last_name` - Фамилия
- `password` - Зашифрованный пароль

### UserProfile
- `user` - Связь с User
- `is_online` - Статус онлайн
- `last_seen` - Время последнего входа
- `avatar` - URL аватара (по умолчанию placeholder)

### ChatRoom
- `name` - Название комнаты
- `description` - Описание
- `created_at` - Дата создания
- `participants` - Участники (связь many-to-many с User)

### Message
- `room` - Комната чата
- `user` - Отправитель
- `content` - Содержание сообщения
- `timestamp` - Время отправки
- `is_read` - Статус прочтения

## JWT Аутентификация

Проект использует JWT токены для аутентификации:

- **Access Token** - Живет 1 час, используется для API запросов
- **Refresh Token** - Живет 7 дней, используется для обновления access токена

### Использование токенов

1. После регистрации/входа получаете пару токенов
2. Включайте access токен в заголовок каждого защищенного запроса:
   ```
   Authorization: Bearer <access_token>
   ```
3. Когда access токен истекает, используйте refresh токен для получения нового
4. При выходе добавьте refresh токен в blacklist

## Настройки CORS

Настроены для разработки:
- Разрешены запросы с `localhost:3000` и `127.0.0.1:3000`
- В production нужно будет ограничить домены

## Безопасность

- Пароли хранятся в зашифрованном виде (Django встроенное хеширование)
- JWT токены с автоматической ротацией
- CORS защита
- Валидация данных на уровне сериализаторов
- Права доступа на уровне API views

## Разработка

### Добавление новых endpoints

1. Создайте view в соответствующем `views.py`
2. Добавьте serializer в `serializers.py` (если нужен)
3. Зарегистрируйте URL в `urls.py`
4. Обновите документацию

### Тестирование API

Используйте инструменты типа Postman, curl или Django REST framework браузерный интерфейс:
`http://127.0.0.1:8000/api/`

### Подробная документация API

См. файл `API_DOCUMENTATION.md` для детального описания всех endpoints с примерами запросов и ответов.

## Production настройки

Перед деплоем в production:

1. Установите `DEBUG = False` в `settings.py`
2. Настройте `ALLOWED_HOSTS`
3. Используйте PostgreSQL или другую продакшн БД
4. Настройте статические файлы
5. Используйте HTTPS
6. Настройте правильные CORS домены
7. Используйте переменные окружения для секретных ключей