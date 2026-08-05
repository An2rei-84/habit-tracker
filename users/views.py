"""
Views для авторизации и регистрации пользователей
"""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя

    POST /api/users/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        """
        Создаёт пользователя и возвращает JWT токены
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомный view для получения токена

    POST /api/users/token/
    """
    serializer_class = None  # Используем стандартный serializer из simplejwt

    def post(self, request, *args, **kwargs):
        """
        Возвращает JWT токены при успешной авторизации
        """
        response = super().post(request, *args, **kwargs)

        # Добавляем информацию о пользователе в ответ
        if response.status_code == status.HTTP_200_OK:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()

            # Декодируем токен для получения user_id
            token = response.data['access']
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)

            response.data['user'] = UserSerializer(user).data

        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и редактирование профиля пользователя

    GET /api/users/profile/
    PUT/PATCH /api/users/profile/
    """
    serializer_class = UserSerializer

    def get_object(self):
        """
        Возвращает текущего авторизованного пользователя
        """
        return self.request.user
