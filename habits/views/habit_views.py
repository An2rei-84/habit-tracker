"""
Views для Habit Tracker API
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit
from habits.permissions.habit_permissions import IsOwnerOrReadOnly
from habits.serializers.habit_serializers import (
    HabitCreateSerializer,
    HabitDetailSerializer,
    HabitListSerializer,
    HabitUpdateSerializer,
)


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с привычками

    Эндпоинты:
    - GET /api/habits/ - список привычек текущего пользователя (с пагинацией)
    - POST /api/habits/ - создание новой привычки
    - GET /api/habits/{id}/ - детальный просмотр привычки
    - PUT/PATCH /api/habits/{id}/ - редактирование привычки
    - DELETE /api/habits/{id}/ - удаление привычки
    - GET /api/habits/public/ - список публичных привычек
    """

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        """
        Возвращает permissions в зависимости от action
        Для публичного списка разрешён доступ для неавторизованных
        """
        if self.action == "public":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Возвращает_queryset в зависимости от action
        """
        user = self.request.user

        if self.action == "public":
            # Для публичных привычек показываем все публичные привычки
            return Habit.objects.filter(is_public=True).select_related("user", "related_habit")
        else:
            # Для остальных действий - только привычки текущего пользователя
            return Habit.objects.filter(user=user).select_related("related_habit")

    def get_serializer_class(self):
        """
        Выбирает сериализатор в зависимости от action
        """
        if self.action == "list":
            return HabitListSerializer
        elif self.action == "retrieve":
            return HabitDetailSerializer
        elif self.action == "create":
            return HabitCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return HabitUpdateSerializer
        return HabitDetailSerializer

    def perform_create(self, serializer):
        """
        При создании привычки автоматически привязываем текущего пользователя
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="my")
    def my_habits(self, request):
        """
        Получить список привычек текущего пользователя

        GET /api/habits/my/
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = HabitListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HabitListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="public")
    def public(self, request):
        """
        Получить список публичных привычек

        GET /api/habits/public/
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = HabitListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HabitListSerializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Переопределяем list для показа привычек текущего пользователя
        """
        return self.my_habits(request)
