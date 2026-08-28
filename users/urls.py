"""
URL configuration для users app
"""

from django.urls import path

from users.views import CustomTokenObtainPairView, RegisterView, UserProfileView

app_name = "users"

urlpatterns = [
    # Регистрация
    path("register/", RegisterView.as_view(), name="register"),
    # Авторизация (JWT token)
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Профиль пользователя
    path("profile/", UserProfileView.as_view(), name="profile"),
]
