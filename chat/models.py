from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatRoom(models.Model):
    CHAT_TYPES = [
        ('direct', 'Прямой чат'),
        ('group', 'Групповой чат'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPES, default='direct')
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        
    def is_direct_chat(self):
        """Проверяет, является ли чат прямым (1-на-1)"""
        return self.chat_type == 'direct' and self.participants.count() == 2
        
    def get_other_participant(self, user):
        """Получает другого участника для прямого чата"""
        if self.is_direct_chat():
            return self.participants.exclude(id=user.id).first()
        return None


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'

    class Meta:
        ordering = ['timestamp']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    avatar = models.URLField(blank=True, null=True, default='https://via.placeholder.com/150?text=Avatar')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        if self.is_online:
            self.last_seen = timezone.now()
        # Если аватар не задан, используем стандартный
        if not self.avatar:
            self.avatar = 'https://via.placeholder.com/150?text=Avatar'
        super().save(*args, **kwargs)
