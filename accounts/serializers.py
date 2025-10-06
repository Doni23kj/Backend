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
    avatar = serializers.URLField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def validate_email(self, value):
        """Проверяем уникальность email"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value


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
                'avatar': profile.avatar
            }
        except UserProfile.DoesNotExist:
            return {
                'is_online': False,
                'last_seen': None,
                'avatar': None
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