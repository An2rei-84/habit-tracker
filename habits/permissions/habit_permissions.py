"""
Пермишены для контроля доступа к привычкам
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение всем (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем запись (POST, PUT, PATCH, DELETE) только владельцу
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Разрешение только для владельца объекта.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPublicHabitOrOwner(permissions.BasePermission):
    """
    Разрешение на чтение публичных привычек или собственных.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение публичных привычек
        if obj.is_public and request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем все операции для владельца
        return obj.user == request.user
