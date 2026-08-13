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
    now = timezone.localtime()

    print("=== TASK DEBUG ===")
    print(f"now: {now}")
    print(f"now.time(): {now.time()}")

    # Получаем активные привычки
    habits = Habit.objects.filter(
        is_active=True,
        frequency__gte=1,
        frequency__lte=7,
    ).select_related("owner", "place", "linked_habit")

    print(f"Total habits found: {habits.count()}")

    for habit in habits:
        print(f"Habit: {habit.id} - action: {habit.action} - time: {habit.time}")

    sent_count = 0
    for habit in habits:
        habit_time = habit.time
        habit_datetime = datetime.combine(now.date(), habit_time)
        habit_datetime = timezone.make_aware(
            habit_datetime, timezone.get_current_timezone()
        )

        time_diff = (habit_datetime - now).total_seconds()

        print(f"Habit {habit.id}: time_diff = {time_diff} seconds")
        print(f"  habit_time: {habit_time}")
        print(f"  habit_datetime: {habit_datetime}")
        print(f"  now: {now}")
        print(f"  condition: 0 <= {time_diff} <= 300")

        if 0 <= time_diff <= 300:
            print(f"✅ Habit {habit.id}: IN RANGE!")

            try:
                telegram_user = TelegramUser.objects.get(
                    user=habit.owner, is_active=True
                )
                print(f"✅ Telegram user found: {telegram_user.chat_id}")

                # Формируем сообщение
                message = f"⏰ Напоминание о привычке!\n\nДействие: {habit.action}\nВремя: {habit.time.strftime('%H:%M')}"

                result = bot.send_message(telegram_user.chat_id, message)
                print(f"Bot send_message result: {result}")

                if result and result.get("ok"):
                    sent_count += 1
                    logger.info(f"Notification sent to {telegram_user.chat_id}")
                else:
                    logger.error(f"Failed to send notification to {telegram_user.chat_id}")

            except TelegramUser.DoesNotExist:
                logger.warning(f"Telegram user not found for {habit.owner.email}")
                print(f"❌ Telegram user NOT FOUND for {habit.owner.email}")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Habit {habit.id}: NOT in range")

    print(f"=== TASK END: Sent {sent_count} notifications ===")
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
