import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from django.utils import timezone
from apps.telegram_bot.tasks import send_habit_notifications
from apps.telegram_bot.models import TelegramUser


@pytest.mark.django_db
class TestTelegramTasks:

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_success(
            self, mock_bot, user_factory, habit_factory, place_factory
    ):
        user = user_factory()
        place = place_factory(owner=user)

        TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

        now = timezone.now()
        habit_time = (now + timedelta(seconds=1)).time()

        habit = habit_factory(
            owner=user,
            place=place,
            name="Test Habit",
            action="Test Action",
            time=habit_time,
            frequency=1,
            is_active=True
        )

        print(f"Habit time: {habit.time}")
        print(f"Current time: {timezone.now().time()}")
        from datetime import datetime
        habit_datetime = datetime.combine(timezone.now().date(), habit.time)
        habit_datetime = timezone.make_aware(habit_datetime, timezone.get_current_timezone())
        print(f"Time diff: {(habit_datetime - timezone.now()).total_seconds()}")

        mock_bot.send_message.return_value = {"ok": True}

        result = send_habit_notifications()

        assert "Sent 1 notifications" in result
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args[0]
        assert call_args[0] == "123456789"
        assert "Test Action" in call_args[1]

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_no_habits(self, mock_bot, user_factory):
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

        result = send_habit_notifications()

        assert "Sent 0 notifications" in result
        mock_bot.send_message.assert_not_called()

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_no_telegram_user(
            self, mock_bot, habit_factory, user_factory, place_factory
    ):
        user = user_factory()
        place = place_factory(owner=user)

        now = timezone.now()
        habit = habit_factory(
            owner=user,
            place=place,
            name="Test Habit",
            action="Test Habit",
            time=now.time(),
            frequency=1,
            is_active=True,
        )

        print(f"Habit time: {habit.time}")
        print(f"Current time: {timezone.now().time()}")
        from datetime import datetime
        habit_datetime = datetime.combine(timezone.now().date(), habit.time)
        habit_datetime = timezone.make_aware(habit_datetime, timezone.get_current_timezone())
        print(f"Time diff: {(habit_datetime - timezone.now()).total_seconds()}")

        result = send_habit_notifications()

        assert "Sent 0 notifications" in result
        mock_bot.send_message.assert_not_called()

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_telegram_error(
            self, mock_bot, user_factory, habit_factory, place_factory
    ):
        user = user_factory()
        place = place_factory(owner=user)  #
        TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

        future_time = (timezone.now() + timedelta(seconds=1)).time()

        habit = habit_factory(
            owner=user,
            place=place,
            name="Test Habit",
            action="Test Action",
            time=future_time,
            frequency=1,
            is_active=True
        )

        print(f"Habit time: {habit.time}")
        print(f"Current time: {timezone.now().time()}")
        from datetime import datetime
        habit_datetime = datetime.combine(timezone.now().date(), habit.time)
        habit_datetime = timezone.make_aware(habit_datetime, timezone.get_current_timezone())
        print(f"Time diff: {(habit_datetime - timezone.now()).total_seconds()}")

        mock_bot.send_message.side_effect = Exception("Telegram API error")

        result = send_habit_notifications()

        assert "Sent 0 notifications" in result
        mock_bot.send_message.assert_called_once()

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_habit_not_due(
            self, mock_bot, user_factory, habit_factory, place_factory
    ):
        user = user_factory()
        place = place_factory(owner=user)
        TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

        now = timezone.now()
        future_time = (
            datetime.combine(datetime.today(), now.time()) + timedelta(minutes=10)
        ).time()
        habit_factory(
            owner=user,
            place=place,
            name="Test Habit",
            action="Test Habit",
            time=future_time,
            frequency=1,
            is_active=True,
        )

        result = send_habit_notifications()

        assert "Sent 0 notifications" in result
        mock_bot.send_message.assert_not_called()

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_inactive_habit(
            self, mock_bot, user_factory, habit_factory, place_factory
    ):
        user = user_factory()
        place = place_factory(owner=user)
        TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

        now = timezone.now()
        habit_factory(
            owner=user,
            place=place,
            name="Test Habit",
            action="Test Habit",
            time=now.time(),
            frequency=1,
            is_active=False,
        )

        result = send_habit_notifications()

        assert "Sent 0 notifications" in result
        mock_bot.send_message.assert_not_called()

    @patch("apps.telegram_bot.tasks.bot")
    def test_send_habit_notifications_habit_with_reward(
            self, mock_bot, user_factory, habit_factory, place_factory
    ):
        user = user_factory()
        place = place_factory(owner=user)
        TelegramUser.objects.create(user=user, chat_id="123456789", is_active=True)

        habit = habit_factory(
            owner=user,
            place=place,
            name="Test Habit",
            action="Test Action",
            time=timezone.now().time(),
            frequency=1,
            is_active=True,
            reward="Chocolate"
        )

        print(f"Habit time: {habit.time}")
        print(f"Current time: {timezone.now().time()}")
        from datetime import datetime
        habit_datetime = datetime.combine(timezone.now().date(), habit.time)
        habit_datetime = timezone.make_aware(habit_datetime, timezone.get_current_timezone())
        print(f"Time diff: {(habit_datetime - timezone.now()).total_seconds()}")

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

        linked_habit = habit_factory(
            owner=user,
            place=place,
            name="Linked Habit",
            action="Linked Action",
            is_pleasant=True
        )

        habit = habit_factory(
            owner=user,
            place=place,
            name="Main Habit",
            action="Main Action",
            time=timezone.now().time(),
            frequency=1,
            is_active=True,
            linked_habit=linked_habit
        )

        print(f"Habit time: {habit.time}")
        print(f"Current time: {timezone.now().time()}")
        from datetime import datetime
        habit_datetime = datetime.combine(timezone.now().date(), habit.time)
        habit_datetime = timezone.make_aware(habit_datetime, timezone.get_current_timezone())
        print(f"Time diff: {(habit_datetime - timezone.now()).total_seconds()}")

        mock_bot.send_message.return_value = {"ok": True}

        result = send_habit_notifications()

        assert "Sent 1 notifications" in result
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args[0]
        assert "Linked Action" in call_args[1]
