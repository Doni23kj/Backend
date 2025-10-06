from django.contrib import admin
from .models import ChatRoom, Message, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_seen', 'avatar']
    list_filter = ['is_online', 'last_seen']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_seen']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'participants_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['participants']
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Количество участников'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read', 'room']
    search_fields = ['user__username', 'content', 'room__name']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Содержание'
