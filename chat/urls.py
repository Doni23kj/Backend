from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.ChatRoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', views.ChatRoomDetailView.as_view(), name='room-detail'),
    path('rooms/<int:room_id>/history/', views.chat_history, name='chat-history'),
    path('rooms/<int:room_id>/participants/', views.room_participants_status, name='room-participants'),
    path('messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('online-users/', views.online_users, name='online-users'),
    path('rooms/<int:room_id>/join/', views.join_room, name='join-room'),
    path('rooms/<int:room_id>/leave/', views.leave_room, name='leave-room'),
    path('create-direct-chat/', views.create_direct_chat, name='create-direct-chat'),
]