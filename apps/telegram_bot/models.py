from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_profile'
    )
    chat_id = models.CharField(max_length=100, unique=True, verbose_name='Chat ID')
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Username')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
        indexes = [
            models.Index(fields=['chat_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} ({self.chat_id})"
