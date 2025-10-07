from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from chat.models import UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileUpdateSerializer, UserProfileDetailSerializer,
    ChangePasswordSerializer
)
from chat.serializers import UserSerializer


def get_tokens_for_user(user):
    """Генерирует JWT токены для пользователя"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """Вход пользователя"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Необходимо указать имя пользователя и пароль'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user:
        if user.is_active:
            # Обновляем статус онлайн
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_online = True
            profile.save()
            
            tokens = get_tokens_for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens,
                'message': 'Успешный вход'
            })
        else:
            return Response({
                'error': 'Аккаунт деактивирован'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'Неверное имя пользователя или пароль'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """Выход пользователя"""
    try:
        # Обновляем статус оффлайн
        profile = request.user.profile
        profile.is_online = False
        profile.save()
    except UserProfile.DoesNotExist:
        pass
    
    try:
        # Получаем refresh token из запроса и добавляем в blacklist
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass
    
    return Response({'message': 'Успешный выход'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Получить текущего пользователя"""
    return Response(UserSerializer(request.user).data)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_detail(request):
    """Получить или обновить профиль пользователя"""
    if request.method == 'GET':
        serializer = UserProfileDetailSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Обновляем основную информацию пользователя
        user_serializer = UserProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            context={'request': request}
        )
        
        if user_serializer.is_valid():
            user_serializer.save()
            
            # Обновляем аватар в профиле, если передан
            avatar = request.data.get('avatar')
            if avatar is not None:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.avatar = avatar
                profile.save()
            
            # Возвращаем обновленную информацию
            response_serializer = UserProfileDetailSerializer(request.user)
            return Response({
                'user': response_serializer.data,
                'message': 'Профиль успешно обновлен'
            })
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Смена пароля пользователя"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Пароль успешно изменен'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Поиск пользователей по имени"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({'users': []})
    
    # Поиск по username, first_name, last_name
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id).select_related('profile')[:10]  # Ограничиваем результаты
    
    user_data = []
    for user in users:
        try:
            profile = user.profile
            user_info = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'is_online': profile.is_online,
                'last_seen': profile.last_seen,
                'avatar': profile.avatar or 'https://via.placeholder.com/150?text=Avatar'
            }
        except UserProfile.DoesNotExist:
            user_info = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'is_online': False,
                'last_seen': None,
                'avatar': 'https://via.placeholder.com/150?text=Avatar'
            }
        user_data.append(user_info)
    
    return Response({'users': user_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """Получить список всех пользователей (для поиска и начала чатов)"""
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    user_data = []
    
    for user in users:
        try:
            profile = user.profile
            user_info = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'is_online': profile.is_online,
                'last_seen': profile.last_seen,
                'avatar': profile.avatar or 'https://via.placeholder.com/150?text=Avatar'
            }
        except UserProfile.DoesNotExist:
            user_info = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'is_online': False,
                'last_seen': None,
                'avatar': 'https://via.placeholder.com/150?text=Avatar'
            }
        user_data.append(user_info)
    
    return Response({'users': user_data})
