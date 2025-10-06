# WebSocket API Documentation

## WebSocket Connection

### Подключение к чату
```
ws://127.0.0.1:8000/ws/chat/<room_id>/
```

### Аутентификация
WebSocket использует сессионную аутентификацию Django. Убедитесь, что пользователь аутентифицирован перед подключением.

## Протокол сообщений

### 📤 Отправка сообщений (Client → Server)

#### 1. Отправка текстового сообщения
```json
{
    "type": "chat_message",
    "message": "Привет! Как дела?"
}
```

#### 2. Индикатор печати
```json
{
    "type": "typing",
    "is_typing": true
}
```

#### 3. Отметка сообщений как прочитанных
```json
{
    "type": "mark_read"
}
```

### 📥 Получение сообщений (Server → Client)

#### 1. Новое сообщение
```json
{
    "type": "chat_message",
    "message_id": 123,
    "message": "Привет! Как дела?",
    "user_id": 2,
    "username": "anotheruser",
    "timestamp": "2025-10-03T03:00:00Z",
    "is_read": false
}
```

#### 2. Подтверждение отправки (для отправителя)
```json
{
    "type": "message_sent",
    "message_id": 123,
    "message": "Привет! Как дела?",
    "timestamp": "2025-10-03T03:00:00Z"
}
```

#### 3. Изменение статуса пользователя
```json
{
    "type": "user_status",
    "user_id": 2,
    "username": "anotheruser",
    "is_online": true,
    "message": "anotheruser в сети"
}
```

#### 4. Индикатор печати
```json
{
    "type": "typing_indicator",
    "user_id": 2,
    "username": "anotheruser",
    "is_typing": true
}
```

#### 5. Подтверждение прочтения
```json
{
    "type": "messages_marked_read",
    "room_id": 1
}
```

#### 6. Ошибка
```json
{
    "type": "error",
    "message": "Сообщение не может быть пустым"
}
```

## Управление статусами

### Онлайн статус
- **Online**: Пользователь подключен к WebSocket чата
- **Offline**: Пользователь отключился от WebSocket или закрыл вкладку

### Статусы сообщений
- **is_read = false**: Новое непрочитанное сообщение
- **is_read = true**: Сообщение прочитано получателем

### Автоматические действия
1. При подключении к WebSocket:
   - Пользователь помечается как online
   - Все непрочитанные сообщения от других пользователей отмечаются как прочитанные

2. При отключении от WebSocket:
   - Пользователь помечается как offline
   - Обновляется время последнего визита

## Примеры использования

### JavaScript WebSocket Client

```javascript
// Подключение к WebSocket
const roomId = 1;
const websocket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${roomId}/`);

// Обработка подключения
websocket.onopen = function(event) {
    console.log('Connected to chat room');
};

// Обработка входящих сообщений
websocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'chat_message':
            displayNewMessage(data);
            break;
        case 'message_sent':
            markMessageAsSent(data);
            break;
        case 'user_status':
            updateUserStatus(data);
            break;
        case 'typing_indicator':
            showTypingIndicator(data);
            break;
        case 'error':
            showError(data.message);
            break;
    }
};

// Отправка сообщения
function sendMessage(messageText) {
    websocket.send(JSON.stringify({
        'type': 'chat_message',
        'message': messageText
    }));
}

// Отправка индикатора печати
function sendTypingIndicator(isTyping) {
    websocket.send(JSON.stringify({
        'type': 'typing',
        'is_typing': isTyping
    }));
}

// Отметка сообщений как прочитанных
function markMessagesAsRead() {
    websocket.send(JSON.stringify({
        'type': 'mark_read'
    }));
}

// Обработка отключения
websocket.onclose = function(event) {
    console.log('Disconnected from chat room');
};

// Обработка ошибок
websocket.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```

### Интеграция с React

```jsx
import { useState, useEffect, useRef } from 'react';

function ChatRoom({ roomId, currentUser }) {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [onlineUsers, setOnlineUsers] = useState([]);
    const websocket = useRef(null);

    useEffect(() => {
        // Подключение к WebSocket
        websocket.current = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${roomId}/`);

        websocket.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'chat_message':
                    setMessages(prev => [...prev, data]);
                    break;
                case 'user_status':
                    updateUserStatus(data);
                    break;
                case 'typing_indicator':
                    setIsTyping(data.is_typing && data.user_id !== currentUser.id);
                    break;
            }
        };

        return () => {
            websocket.current?.close();
        };
    }, [roomId]);

    const sendMessage = () => {
        if (newMessage.trim() && websocket.current) {
            websocket.current.send(JSON.stringify({
                'type': 'chat_message',
                'message': newMessage
            }));
            setNewMessage('');
        }
    };

    const handleTyping = () => {
        if (websocket.current) {
            websocket.current.send(JSON.stringify({
                'type': 'typing',
                'is_typing': true
            }));
            
            // Останавливаем индикатор через 2 секунды
            setTimeout(() => {
                websocket.current?.send(JSON.stringify({
                    'type': 'typing',
                    'is_typing': false
                }));
            }, 2000);
        }
    };

    return (
        <div className="chat-room">
            <div className="messages">
                {messages.map(msg => (
                    <div key={msg.message_id} className="message">
                        <strong>{msg.username}:</strong> {msg.message}
                        <small>{new Date(msg.timestamp).toLocaleTimeString()}</small>
                    </div>
                ))}
                {isTyping && <div className="typing">Пользователь печатает...</div>}
            </div>
            
            <div className="message-input">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                            sendMessage();
                        } else {
                            handleTyping();
                        }
                    }}
                    placeholder="Введите сообщение..."
                />
                <button onClick={sendMessage}>Отправить</button>
            </div>
        </div>
    );
}
```

## Безопасность

1. **Аутентификация**: Только аутентифицированные пользователи могут подключаться к WebSocket
2. **Авторизация**: Пользователи могут подключаться только к чатам, участниками которых они являются
3. **Валидация**: Все входящие сообщения проверяются на корректность
4. **Логирование**: Все действия логируются для отладки и мониторинга

## Ограничения

1. **Размер сообщения**: Максимальная длина сообщения определяется моделью Message
2. **Количество подключений**: Ограничено настройками сервера
3. **Channel Layer**: В разработке используется InMemoryChannelLayer (не подходит для production)

## Production настройки

Для production рекомендуется:

1. Использовать Redis Channel Layer:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

2. Настроить правильные CORS заголовки для WebSocket
3. Использовать SSL/TLS (wss://) для WebSocket соединений
4. Настроить мониторинг подключений и производительности