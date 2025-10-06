# Mini Chat API Documentation

## Базовый URL
```
http://127.0.0.1:8000/api/
```

## Аутентификация
Все защищенные endpoints требуют JWT токен в заголовке:
```
Authorization: Bearer <access_token>
```

## Endpoints

### 🔐 Аутентификация (`/api/auth/`)

#### 1. Регистрация
```http
POST /api/auth/register/
```

**Запрос:**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
}
```

**Ответ:**
```json
{
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    },
    "message": "Пользователь успешно зарегистрирован"
}
```

#### 2. Вход в систему
```http
POST /api/auth/login/
```

**Запрос:**
```json
{
    "username": "testuser",
    "password": "securepassword123"
}
```

**Ответ:**
```json
{
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    },
    "message": "Успешный вход"
}
```

#### 3. Выход из системы
```http
POST /api/auth/logout/
```
**Требует аутентификации**

**Запрос:**
```json
{
    "refresh": "refresh_token_here"
}
```

#### 4. Обновление токена
```http
POST /api/auth/token/refresh/
```

**Запрос:**
```json
{
    "refresh": "refresh_token_here"
}
```

**Ответ:**
```json
{
    "access": "new_access_token_here"
}
```

#### 5. Текущий пользователь
```http
GET /api/auth/me/
```
**Требует аутентификации**

**Ответ:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
}
```

#### 6. Профиль пользователя
```http
GET /api/auth/profile/
PUT /api/auth/profile/
```
**Требует аутентификации**

**GET Ответ:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "date_joined": "2025-10-03T03:00:00Z",
    "profile": {
        "is_online": true,
        "last_seen": "2025-10-03T03:00:00Z",
        "avatar": "https://via.placeholder.com/150?text=Avatar"
    }
}
```

**PUT Запрос:**
```json
{
    "first_name": "NewName",
    "last_name": "NewLastName",
    "email": "newemail@example.com",
    "avatar": "https://example.com/avatar.jpg"
}
```

#### 7. Смена пароля
```http
POST /api/auth/change-password/
```
**Требует аутентификации**

**Запрос:**
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

#### 8. Поиск пользователей
```http
GET /api/auth/search/?q=username
```
**Требует аутентификации**

**Ответ:**
```json
{
    "users": [
        {
            "id": 2,
            "username": "anotheruser",
            "first_name": "Another",
            "last_name": "User",
            "full_name": "Another User",
            "is_online": false,
            "last_seen": "2025-10-03T02:30:00Z",
            "avatar": "https://via.placeholder.com/150?text=Avatar"
        }
    ]
}
```

#### 9. Список всех пользователей
```http
GET /api/auth/users/
```
**Требует аутентификации**

### 💬 Чат (`/api/chat/`)

#### 1. Список комнат чата
```http
GET /api/chat/rooms/
POST /api/chat/rooms/
```
**Требует аутентификации**

**GET Ответ:**
```json
[
    {
        "id": 1,
        "name": "Чат: testuser и anotheruser",
        "description": "Прямой чат между testuser и anotheruser",
        "created_at": "2025-10-03T03:00:00Z",
        "participants": [
            {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            }
        ],
        "participants_count": 2
    }
]
```

**POST Запрос:**
```json
{
    "name": "Новая комната",
    "description": "Описание комнаты"
}
```

#### 2. Создание прямого чата
```http
POST /api/chat/create-direct-chat/
```
**Требует аутентификации**

**Запрос:**
```json
{
    "user_id": 2
}
```

**Ответ:**
```json
{
    "room": {
        "id": 1,
        "name": "Чат: testuser и anotheruser",
        "description": "Прямой чат между testuser и anotheruser",
        "created_at": "2025-10-03T03:00:00Z",
        "participants": [...],
        "participants_count": 2
    },
    "message": "Чат успешно создан"
}
```

#### 3. Сообщения
```http
GET /api/chat/messages/?room=1
POST /api/chat/messages/
```
**Требует аутентификации**

**GET Ответ:**
```json
[
    {
        "id": 1,
        "room": 1,
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        },
        "user_username": "testuser",
        "content": "Привет!",
        "timestamp": "2025-10-03T03:00:00Z",
        "is_read": false
    }
]
```

**POST Запрос:**
```json
{
    "room": 1,
    "content": "Привет! Как дела?"
}
```

#### 4. История чата
```http
GET /api/chat/rooms/1/history/
```
**Требует аутентификации**

**Ответ:**
```json
{
    "room": {
        "id": 1,
        "name": "Чат: testuser и anotheruser",
        ...
    },
    "messages": [
        {
            "id": 1,
            "content": "Привет!",
            "user": {...},
            "timestamp": "2025-10-03T03:00:00Z",
            "is_read": true
        }
    ]
}
```

#### 5. Онлайн пользователи
```http
GET /api/chat/online-users/
```
**Требует аутентификации**

**Ответ:**
```json
[
    {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        },
        "is_online": true,
        "last_seen": "2025-10-03T03:00:00Z",
        "avatar": "https://via.placeholder.com/150?text=Avatar"
    }
]
```

## Коды ошибок

- `400 Bad Request` - Неверные данные запроса
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Доступ запрещен
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Внутренняя ошибка сервера

## Примеры использования

### Полный цикл аутентификации

1. **Регистрация:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

2. **Использование API с токеном:**
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer your_access_token_here"
```

3. **Поиск пользователей:**
```bash
curl -X GET "http://127.0.0.1:8000/api/auth/search/?q=test" \
  -H "Authorization: Bearer your_access_token_here"
```

4. **Создание чата:**
```bash
curl -X POST http://127.0.0.1:8000/api/chat/create-direct-chat/ \
  -H "Authorization: Bearer your_access_token_here" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'
```

5. **Отправка сообщения:**
```bash
curl -X POST http://127.0.0.1:8000/api/chat/messages/ \
  -H "Authorization: Bearer your_access_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "content": "Привет! Как дела?"
  }'
```