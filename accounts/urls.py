from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('me/', views.current_user, name='current-user'),
    path('profile/', views.profile_detail, name='profile-detail'),
    path('change-password/', views.change_password, name='change-password'),
    path('users/', views.user_list, name='user-list'),
    path('search/', views.search_users, name='search-users'),
]