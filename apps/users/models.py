import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    is_verified = models.BooleanField(default=False, verbose_name="Подтвержден")
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.email


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="verification_token"
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Токен верификации"
        verbose_name_plural = "Токены верификации"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at
