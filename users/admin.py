"""
Админ-панель для модели User
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админ-панель для модели User
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'telegram_chat_id', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telegram_chat_id']
    ordering = ['username']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('telegram_chat_id', 'phone')}),
    )
