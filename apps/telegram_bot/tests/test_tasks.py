import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from django.utils import timezone
from apps.telegram_bot.tasks import send_habit_notifications
from apps.telegram_bot.models import TelegramUser

@pytest.mark.django_db
class TestTelegramTasks:


@patch("apps.telegram_bot.tasks.bot")
def test_send_habit_notifications_telegram_error(
        self, mock_bot, user_factory, habit_factory, place_factory
):
    user = user_factory()
    place = place_factory(owner=user)
    TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

    habit_time = (timezone.now() + timedelta(seconds=5)).time()  # <-- ИСПРАВЛЕНО

    habit = habit_factory(
        owner=user,
        place=place,
        name="Test Habit",
        action="Test Action",
        time=habit_time,  # <-- ИСПРАВЛЕНО
        frequency=1,
        is_active=True,
        time_to_complete=60,
    )

    mock_bot.send_message.side_effect = Exception("Telegram API error")
    result = send_habit_notifications()

    assert "Sent 0 notifications" in result
    mock_bot.send_message.assert_called_once()


@patch("apps.telegram_bot.tasks.bot")
def test_send_habit_notifications_habit_with_reward(
        self, mock_bot, user_factory, habit_factory, place_factory
):
    user = user_factory()
    place = place_factory(owner=user)
    TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

    habit_time = (timezone.now() + timedelta(seconds=5)).time()  # <-- ИСПРАВЛЕНО

    habit = habit_factory(
        owner=user,
        place=place,
        name="Test Habit",
        action="Test Action",
        time=habit_time,  # <-- ИСПРАВЛЕНО
        frequency=1,
        is_active=True,
        reward="Chocolate",
        time_to_complete=60,
    )

    mock_bot.send_message.return_value = {"ok": True}
    result = send_habit_notifications()

    assert "Sent 1 notifications" in result
    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args[0]
    assert "Chocolate" in call_args[1]


@patch("apps.telegram_bot.tasks.bot")
def test_send_habit_notifications_habit_with_linked_habit(
        self, mock_bot, user_factory, habit_factory, place_factory
):
    user = user_factory()
    place = place_factory(owner=user)
    TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

    habit_time = (timezone.now() + timedelta(seconds=5)).time()  # <-- ИСПРАВЛЕНО

    linked_habit = habit_factory(
        owner=user,
        place=place,
        name="Linked Habit",
        action="Linked Action",
        is_pleasant=True,
        time_to_complete=60,
    )

    habit = habit_factory(
        owner=user,
        place=place,
        name="Main Habit",
        action="Main Action",
        time=habit_time,  # <-- ИСПРАВЛЕНО
        frequency=1,
        is_active=True,
        linked_habit=linked_habit,
        time_to_complete=60,
    )

    mock_bot.send_message.return_value = {"ok": True}
    result = send_habit_notifications()

    assert "Sent 1 notifications" in result
    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args[0]
    assert "Linked Action" in call_args[1]
