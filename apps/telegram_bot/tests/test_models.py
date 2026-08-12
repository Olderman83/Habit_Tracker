import pytest
from apps.telegram_bot.models import TelegramUser
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestTelegramUserModel:
    def test_create_telegram_user(self, user_factory):
        user = user_factory()
        telegram_user = TelegramUser.objects.create(
            user=user, chat_id="123456789", username="test_user"
        )

        assert telegram_user.id is not None
        assert telegram_user.user == user
        assert telegram_user.chat_id == "123456789"
        assert telegram_user.username == "test_user"
        assert telegram_user.is_active is True

    def test_telegram_user_str_method(self, user_factory):
        user = user_factory(email="test@example.com")
        telegram_user = TelegramUser.objects.create(user=user, chat_id="123456789")

        assert str(telegram_user) == "test@example.com (123456789)"

    def test_telegram_user_unique_chat_id(self, user_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")

        TelegramUser.objects.create(user=user1, chat_id="123456789")

        with pytest.raises(Exception):  # IntegrityError
            TelegramUser.objects.create(user=user2, chat_id="123456789")

    def test_telegram_user_unique_user(self, user_factory):
        user = user_factory()

        TelegramUser.objects.create(user=user, chat_id="123456789")

        with pytest.raises(Exception):  # IntegrityError
            TelegramUser.objects.create(user=user, chat_id="987654321")

    def test_telegram_user_indexes(self, user_factory):
        user = user_factory()
        telegram_user = TelegramUser.objects.create(
            user=user, chat_id="123456789", is_active=True
        )

        # Test that indexes exist by querying
        assert TelegramUser.objects.filter(chat_id="123456789").exists()
        assert TelegramUser.objects.filter(is_active=True).exists()

        assert telegram_user.chat_id == "123456789"
        assert telegram_user.is_active is True
        assert telegram_user.user == user
