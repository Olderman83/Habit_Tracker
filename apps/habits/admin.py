from django.contrib import admin
from .models import Habit, Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'action', 'owner', 'time', 'is_pleasant',
        'is_public', 'is_active', 'frequency', 'time_to_complete'
    )
    list_filter = ('is_pleasant', 'is_public', 'is_active', 'owner')
    search_fields = ('action', 'reward')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'action', 'place', 'time')
        }),
        ('Тип привычки', {
            'fields': ('is_pleasant', 'linked_habit', 'reward')
        }),
        ('Настройки выполнения', {
            'fields': ('frequency', 'time_to_complete')
        }),
        ('Дополнительно', {
            'fields': ('is_public', 'is_active')
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
