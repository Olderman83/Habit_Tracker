import pytest
from unittest.mock import patch
from django.utils import timezone
from datetime import datetime, timedelta
from apps.telegram_bot.tasks import send_habit_notifications
from apps.telegram_bot.models import TelegramUser


@pytest.mark.django_db
class TestTelegramTasks:
    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_success(self, mock_bot, user_factory, habit_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        # Create habit due now
        now = timezone.now()
        habit = habit_factory(
            owner=user,
            action='Test Habit',
            time=now.time(),
            frequency=1,
            is_active=True
        )

        # Mock bot response
        mock_bot.send_message.return_value = {'ok': True}

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 1 notifications' in result
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args[0]
        assert call_args[0] == '123456789'  # chat_id
        assert habit.action in call_args[1]  # message

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_no_habits(self, mock_bot, user_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 0 notifications' in result
        mock_bot.send_message.assert_not_called()

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_no_telegram_user(self, mock_bot, habit_factory, user_factory):
        # Setup
        user = user_factory()  # No TelegramUser created

        now = timezone.now()
        habit_factory(
            owner=user,
            action='Test Habit',
            time=now.time(),
            frequency=1,
            is_active=True
        )

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 0 notifications' in result
        mock_bot.send_message.assert_not_called()

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_telegram_error(self, mock_bot, user_factory, habit_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        now = timezone.now()
        habit_factory(
            owner=user,
            action='Test Habit',
            time=now.time(),
            frequency=1,
            is_active=True
        )

        # Mock bot error
        mock_bot.send_message.return_value = {'ok': False}

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 0 notifications' in result
        mock_bot.send_message.assert_called_once()

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_habit_not_due(self, mock_bot, user_factory, habit_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        # Create habit due in 10 minutes (should not be notified)
        now = timezone.now()
        future_time = (datetime.combine(datetime.today(), now.time()) + timedelta(minutes=10)).time()
        habit_factory(
            owner=user,
            action='Test Habit',
            time=future_time,
            frequency=1,
            is_active=True
        )

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 0 notifications' in result
        mock_bot.send_message.assert_not_called()

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_inactive_habit(self, mock_bot, user_factory, habit_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        now = timezone.now()
        habit_factory(
            owner=user,
            action='Test Habit',
            time=now.time(),
            frequency=1,
            is_active=False  # Inactive habit
        )

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 0 notifications' in result
        mock_bot.send_message.assert_not_called()

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_habit_with_reward(self, mock_bot, user_factory, habit_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        now = timezone.now()
        habit_factory(
            owner=user,
            action='Test Habit',
            time=now.time(),
            frequency=1,
            is_active=True,
            reward='Watch movie'
        )

        mock_bot.send_message.return_value = {'ok': True}

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 1 notifications' in result
        call_args = mock_bot.send_message.call_args[0]
        assert 'Вознаграждение' in call_args[1]

    @patch('apps.telegram_bot.tasks.bot')
    def test_send_habit_notifications_habit_with_linked_habit(self, mock_bot, user_factory, habit_factory):
        # Setup
        user = user_factory()
        TelegramUser.objects.create(user=user, chat_id='123456789', is_active=True)

        now = timezone.now()
        linked_habit = habit_factory(owner=user, is_pleasant=True, action='Pleasant Habit')
        habit_factory(
            owner=user,
            action='Test Habit',
            time=now.time(),
            frequency=1,
            is_active=True,
            linked_habit=linked_habit
        )

        mock_bot.send_message.return_value = {'ok': True}

        # Execute task
        result = send_habit_notifications()

        # Assert
        assert 'Sent 1 notifications' in result
        call_args = mock_bot.send_message.call_args[0]
        assert 'Награда' in call_args[1]
        assert 'Pleasant Habit' in call_args[1]
