from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.db import models
from .models import ChatRoom, Message, UserProfile
from .serializers import (
    ChatRoomSerializer, MessageSerializer, 
    CreateMessageSerializer, UserProfileSerializer
)


class ChatRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        room = serializer.save()
        room.participants.add(self.request.user)


class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateMessageSerializer
        return MessageSerializer

    def get_queryset(self):
        room_id = self.request.query_params.get('room')
        if room_id:
            return Message.objects.filter(
                room_id=room_id,
                room__participants=self.request.user
            ).order_by('timestamp')
        return Message.objects.filter(room__participants=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def online_users(request):
    """Получить список онлайн пользователей"""
    online_profiles = UserProfile.objects.filter(is_online=True).select_related('user')
    serializer = UserProfileSerializer(online_profiles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_room(request, room_id):
    """Присоединиться к комнате чата"""
    try:
        room = ChatRoom.objects.get(id=room_id)
        room.participants.add(request.user)
        return Response({'message': 'Успешно присоединились к комнате'})
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Комната не найдена'}, status=404)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_room(request, room_id):
    """Покинуть комнату чата"""
    try:
        room = ChatRoom.objects.get(id=room_id)
        room.participants.remove(request.user)
        return Response({'message': 'Вы покинули комнату'})
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Комната не найдена'}, status=404)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_direct_chat(request):
    """Создать прямой чат с другим пользователем"""
    other_user_id = request.data.get('user_id')
    
    if not other_user_id:
        return Response({'error': 'Необходимо указать ID пользователя'}, status=400)
    
    try:
        other_user = User.objects.get(id=other_user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)
    
    if other_user == request.user:
        return Response({'error': 'Нельзя создать чат с самим собой'}, status=400)
    
    # Проверяем, существует ли уже прямой чат между этими пользователями
    existing_room = ChatRoom.objects.filter(
        chat_type='direct',
        participants=request.user
    ).filter(
        participants=other_user
    ).annotate(
        participant_count=models.Count('participants')
    ).filter(participant_count=2).first()
    
    if existing_room:
        return Response({
            'room': ChatRoomSerializer(existing_room).data,
            'message': 'Чат уже существует'
        })
    
    # Создаем новый прямой чат
    room_name = f"Чат: {request.user.username} и {other_user.username}"
    room = ChatRoom.objects.create(
        name=room_name,
        description=f"Прямой чат между {request.user.username} и {other_user.username}",
        chat_type='direct'
    )
    room.participants.add(request.user, other_user)
    
    return Response({
        'room': ChatRoomSerializer(room).data,
        'message': 'Чат успешно создан'
    }, status=201)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_history(request, room_id):
    """Получить историю сообщений для конкретной комнаты"""
    try:
        room = ChatRoom.objects.get(id=room_id, participants=request.user)
        messages = Message.objects.filter(room=room).order_by('timestamp')
        
        # Отмечаем сообщения как прочитанные
        messages.filter(is_read=False).exclude(user=request.user).update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        room_serializer = ChatRoomSerializer(room, context={'request': request})
        
        return Response({
            'room': room_serializer.data,
            'messages': serializer.data
        })
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Комната не найдена'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def room_participants_status(request, room_id):
    """Получить статус участников конкретной комнаты"""
    try:
        room = ChatRoom.objects.get(id=room_id, participants=request.user)
        participants = room.participants.all().select_related('profile')
        
        participants_data = []
        for user in participants:
            try:
                profile = user.profile
                participant_info = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_online': profile.is_online,
                    'last_seen': profile.last_seen,
                    'avatar': profile.avatar
                }
            except UserProfile.DoesNotExist:
                participant_info = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_online': False,
                    'last_seen': None,
                    'avatar': 'https://via.placeholder.com/150?text=Avatar'
                }
            participants_data.append(participant_info)
            
        return Response({
            'room_id': room_id,
            'participants': participants_data
        })
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Комната не найдена'}, status=404)
