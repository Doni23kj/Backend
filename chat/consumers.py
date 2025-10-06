import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message, UserProfile

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Проверяем аутентификацию
        if not self.user.is_authenticated:
            await self.close()
            return

        # Проверяем доступ к комнате
        room_access = await self.check_room_access()
        if not room_access:
            await self.close()
            return

        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Обновляем статус пользователя на онлайн
        await self.set_user_online(True)

        await self.accept()

        # Уведомляем о подключении
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status_update',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_online': True,
            }
        )

        # Отмечаем сообщения как прочитанные
        await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Покидаем группу
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            # Обновляем статус на оффлайн
            await self.set_user_online(False)

            # Уведомляем об отключении
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status_update',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_online': False,
                }
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                message_content = data.get('message', '').strip()
                
                if not message_content:
                    await self.send_error("Сообщение не может быть пустым")
                    return
                
                # Сохраняем сообщение
                saved_message = await self.save_message(message_content)
                
                if saved_message:
                    # Отправляем в группу
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message_id': saved_message['id'],
                            'message': saved_message['content'],
                            'user_id': saved_message['user_id'],
                            'username': saved_message['username'],
                            'timestamp': saved_message['timestamp'],
                        }
                    )
                    
            elif message_type == 'typing':
                is_typing = data.get('is_typing', False)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': is_typing
                    }
                )
                
            elif message_type == 'mark_read':
                await self.mark_messages_as_read()
                await self.send(text_data=json.dumps({
                    'type': 'messages_marked_read',
                    'room_id': self.room_id
                }))
                
        except json.JSONDecodeError:
            await self.send_error("Неверный формат JSON")
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send_error("Произошла ошибка")

    async def chat_message(self, event):
        """Отправка сообщения"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    async def user_status_update(self, event):
        """Обновление статуса пользователя"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_online': event['is_online'],
            }))

    async def typing_indicator(self, event):
        """Индикатор печати"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    async def send_error(self, error_message):
        """Отправка ошибки"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))

    @database_sync_to_async
    def check_room_access(self):
        """Проверка доступа к комнате"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message_content):
        """Сохранение сообщения"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message_obj = Message.objects.create(
                room=room,
                user=self.user,
                content=message_content
            )
            return {
                'id': message_obj.id,
                'content': message_obj.content,
                'user_id': message_obj.user.id,
                'username': message_obj.user.username,
                'timestamp': message_obj.timestamp.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def mark_messages_as_read(self):
        """Отметка сообщений как прочитанных"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            Message.objects.filter(
                room=room,
                is_read=False
            ).exclude(
                user=self.user
            ).update(is_read=True)
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")

    @database_sync_to_async
    def set_user_online(self, is_online):
        """Установка статуса пользователя"""
        try:
            profile, created = UserProfile.objects.get_or_create(user=self.user)
            profile.is_online = is_online
            profile.save()
        except Exception as e:
            logger.error(f"Error updating user status: {e}")