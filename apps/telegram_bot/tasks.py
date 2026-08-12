import logging
from celery import shared_task
from django.utils import timezone
from datetime import datetime
from .models import TelegramUser
from apps.habits.models import Habit
from .bot import bot

logger = logging.getLogger(__name__)


@shared_task
def send_habit_notifications():
    """Send notifications about habits that need to be performed"""
    now = timezone.now()

    # Получаем активные привычки
    habits = Habit.objects.filter(
        is_active=True,
        frequency__gte=1,
        frequency__lte=7,
    ).select_related("owner", "place", "linked_habit")

    logger.info(f"Checking {habits.count()} habits for notifications")

    sent_count = 0
    for habit in habits:
        # Проверяем, нужно ли напомнить о привычке сегодня
        habit_time = habit.time

        # Создаем datetime для времени привычки на сегодня
        habit_datetime = datetime.combine(now.date(), habit_time)
        habit_datetime = timezone.make_aware(
            habit_datetime, timezone.get_current_timezone()
        )

        # Проверяем, что время привычки в пределах следующих 5 минут
        time_diff = (habit_datetime - now).total_seconds()

        if 0 <= time_diff <= 300:  # 5 minutes
            logger.info(
                f"Time to perform habit: {habit.action} for user {habit.owner.email}"
            )

            # Отправляем уведомление в Telegram
            try:
                telegram_user = TelegramUser.objects.get(
                    user=habit.owner, is_active=True
                )

                # Формируем сообщение
                message_lines = [
                    "⏰ <b>Напоминание о привычке!</b>",
                    "",
                    f"<b>Действие:</b> {habit.action}",
                    f"<b>Время:</b> {habit.time.strftime('%H:%M')}",
                ]

                if habit.place:
                    message_lines.append(f"<b>Место:</b> {habit.place.name}")

                message_lines.append(
                    f"<b>Периодичность:</b> Каждые {habit.frequency} день(дней)"
                )

                if habit.reward:
                    message_lines.append(f"<b>Вознаграждение:</b> {habit.reward}")
                elif habit.linked_habit:
                    message_lines.append(f"<b>Награда:</b> {habit.linked_habit.action}")

                message_lines.append("")
                message_lines.append("Приступайте к выполнению прямо сейчас! 💪")

                message = "\n".join(message_lines)

                result = bot.send_message(telegram_user.chat_id, message)
                if result and result.get("ok"):
                    sent_count += 1
                    logger.info(f"Notification sent to {telegram_user.chat_id}")
                else:
                    logger.error(
                        f"Failed to send notification to {telegram_user.chat_id}"
                    )

            except TelegramUser.DoesNotExist:
                logger.warning(f"Telegram user not found for {habit.owner.email}")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")

    logger.info(f"Sent {sent_count} notifications")
    return f"Sent {sent_count} notifications"


@shared_task
def test_telegram_notification(chat_id, message="Test notification"):
    """Test task for sending Telegram messages"""
    try:
        result = bot.send_message(chat_id, message)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Test notification failed: {e}")
        return {"success": False, "error": str(e)}
