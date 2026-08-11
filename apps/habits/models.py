from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_habit(value):
    from apps.habits.models import Habit

    # Если это создание новой привычки
    if Habit.objects.filter(name=value).exists():
        raise ValidationError(f"Привычка с названием '{value}' уже существует")


class Place(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название места')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='places',
        verbose_name='Владелец'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return self.name


class Habit(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Владелец'
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='habits',
        verbose_name='Место выполнения'
    )
    name = models.CharField(max_length=100, verbose_name='Название привычки',
                            help_text='Уникальное название для привычки')
    action = models.CharField(max_length=255, verbose_name='Действие')
    time = models.TimeField(verbose_name='Время выполнения')

    is_pleasant = models.BooleanField(default=False, verbose_name='Приятная привычка')

    linked_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_from',
        verbose_name='Связанная привычка',
        help_text='Указывается для полезных привычек, должна быть приятной'
    )

    frequency = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (дни)',
        help_text='От 1 до 7 дней'
    )

    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение',
        help_text='Заполняется для полезных привычек без связанной привычки'
    )

    time_to_complete = models.PositiveIntegerField(
        default=60,
        verbose_name='Время на выполнение (секунды)',
        help_text='Не более 120 секунд'
    )

    is_public = models.BooleanField(default=False, verbose_name='Публичная привычка')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['time']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_active']),
            models.Index(fields=['owner', 'is_active']),
        ]

    def __str__(self):
        return f"{self.action} ({self.time})"

    def clean(self):
        if self.pk is None:  # Создание
            if Habit.objects.filter(owner=self.owner, name=self.name).exists():
                raise ValidationError(
                    f"У вас уже есть привычка с названием '{self.name}'"
                )
        else:  # Обновление
            if Habit.objects.exclude(pk=self.pk).filter(owner=self.owner, name=self.name).exists():
                raise ValidationError(
                    f"У вас уже есть привычка с названием '{self.name}'"
                )

        if self.time_to_complete > 120:
            raise ValidationError({
                'time_to_complete': 'Время на выполнение не может превышать 120 секунд'
            })

            # Валидация frequency (от 1 до 7 дней)
        if self.frequency < 1 or self.frequency > 7:
            raise ValidationError({
                'frequency': 'Периодичность должна быть от 1 до 7 дней'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
