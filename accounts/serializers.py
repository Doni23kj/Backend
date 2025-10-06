from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from chat.models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("Аккаунт деактивирован")
            else:
                raise serializers.ValidationError("Неверное имя пользователя или пароль")
        else:
            raise serializers.ValidationError("Необходимо указать имя пользователя и пароль")

        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления профиля пользователя"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def validate_email(self, value):
        """Проверяем уникальность email"""
        user = self.context['request'].user
        
        # Если email пустой, не проверяем уникальность
        if not value or value.strip() == '':
            return value
            
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value
    
    def update(self, instance, validated_data):
        """Обновляем пользователя и его профиль"""
        # Обновляем основные поля пользователя
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Извлекаем дополнительные данные из запроса
        request_data = self.context['request'].data
        bio = request_data.get('bio')
        
        # Обновляем профиль только если есть данные для обновления
        if bio is not None:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            profile.bio = bio
            profile.save()
            print(f"Updated profile bio: {bio}")  # Отладка
        
        return instance


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Детальная информация о профиле пользователя"""
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'profile']
        read_only_fields = ['id', 'username', 'date_joined']
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'is_online': profile.is_online,
                'last_seen': profile.last_seen,
                'avatar': profile.get_avatar_url(),
                'bio': profile.bio or ''  # Добавляем bio
            }
        except UserProfile.DoesNotExist:
            return {
                'is_online': False,
                'last_seen': None,
                'avatar': f'https://via.placeholder.com/150?text={obj.username[0].upper()}',
                'bio': ''  # Добавляем bio для случая, когда профиль не существует
            }


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer для смены пароля"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Новые пароли не совпадают")
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AvatarUploadSerializer(serializers.Serializer):
    """Serializer для загрузки аватара"""
    avatar = serializers.ImageField(required=False)
    avatar_url = serializers.URLField(required=False)
    
    def validate(self, data):
        request = self.context['request']
        # Проверяем наличие данных в FILES или в data
        has_file = 'avatar' in request.FILES
        has_url = 'avatar_url' in request.data and request.data['avatar_url'].strip()
        
        if not has_file and not has_url:
            raise serializers.ValidationError("Необходимо указать либо файл аватара, либо URL")
        return data
    
    def save(self):
        user = self.context['request'].user
        request = self.context['request']
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Приоритет у загружаемого файла
        if 'avatar' in request.FILES:
            profile.avatar_file = request.FILES['avatar']
            # Очищаем URL аватара, если загружаем файл
            profile.avatar = ''
            print(f"Uploaded avatar file: {profile.avatar_file}")
        elif 'avatar_url' in request.data and request.data['avatar_url'].strip():
            profile.avatar = request.data['avatar_url']
            # Очищаем файл аватара, если задаём URL
            profile.avatar_file = None
            print(f"Set avatar URL: {profile.avatar}")
        
        profile.save()
        return profile