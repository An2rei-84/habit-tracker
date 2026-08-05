"""
Сериализаторы для модели User
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра пользователя
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'telegram_chat_id',
            'phone'
        ]
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'telegram_chat_id',
            'phone'
        ]

    def validate(self, data):
        """
        Проверка совпадения паролей
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают'
            })

        return data

    def create(self, validated_data):
        """
        Создаёт пользователя с зашифрованным паролем
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для JWT токенов
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавляем кастомные claims
        token['username'] = user.username
        token['email'] = user.email

        return token
