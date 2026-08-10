"""
Админ-панель для модели Habit
"""

from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Habit
    """

    list_display = [
        "action",
        "user",
        "place",
        "time",
        "is_pleasant",
        "periodicity",
        "duration_to_complete",
        "is_public",
        "created_at",
    ]
    list_filter = ["is_pleasant", "is_public", "created_at", "periodicity"]
    search_fields = ["action", "place", "reward", "user__username"]
    list_editable = ["is_pleasant", "is_public", "periodicity"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Основная информация", {"fields": ("user", "action", "place", "time")}),
        ("Параметры привычки", {"fields": ("is_pleasant", "related_habit", "periodicity", "duration_to_complete")}),
        ("Вознаграждение", {"fields": ("reward",)}),
        ("Доступ", {"fields": ("is_public",)}),
        ("Метаданные", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        """
        Показываем все привычки суперадминистратору,
        а обычным пользователям - только их собственные.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
