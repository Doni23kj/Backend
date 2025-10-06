from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatRoom, Message, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'is_online', 'last_seen', 'avatar']


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participants_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'chat_type', 'created_at', 
            'participants', 'participants_count', 'other_participant', 'unread_count'
        ]

    def get_participants_count(self, obj):
        return obj.participants.count()
        
    def get_other_participant(self, obj):
        """Для прямых чатов возвращает другого участника"""
        request = self.context.get('request')
        if request and obj.chat_type == 'direct':
            other_user = obj.get_other_participant(request.user)
            if other_user:
                return UserSerializer(other_user).data
        return None
        
    def get_unread_count(self, obj):
        """Количество непрочитанных сообщений для текущего пользователя"""
        request = self.context.get('request')
        if request:
            return Message.objects.filter(
                room=obj,
                is_read=False
            ).exclude(user=request.user).count()
        return 0


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'user', 'user_username', 'content', 'timestamp', 'is_read']
        read_only_fields = ['user', 'timestamp']


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['room', 'content']