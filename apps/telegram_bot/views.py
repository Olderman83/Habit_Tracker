import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import TelegramUser
from apps.users.models import User
from .bot import bot

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    """Handle Telegram webhook updates"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            logger.info(f"Received webhook: {data}")

            if 'message' in data and data['message'].get('text') == '/start':
                chat_id = data['message']['chat']['id']
                user_data = data['message']['from']
                username = user_data.get('username', '')
                first_name = user_data.get('first_name', '')
                last_name = user_data.get('last_name', '')

                # Используем username
                logger.info(f"User {username} (ID: {chat_id}) started the bot")

                # Создаем или обновляем запись о пользователе
                telegram_user, created = TelegramUser.objects.get_or_create(
                    chat_id=chat_id,
                    defaults={
                        'username': username,
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                )

                if created:
                    logger.info(f"New Telegram user created: {username}")
                else:
                    # Обновляем данные
                    telegram_user.username = username
                    telegram_user.first_name = first_name
                    telegram_user.last_name = last_name
                    telegram_user.save()

                # Ищем связанного пользователя
                user = User.objects.filter(telegram_chat_id=chat_id).first()

                if user:
                    greeting = f"С возвращением, {user.first_name or username}!"
                else:
                    greeting = "Добро пожаловать!"

                response_text = f"""<b>{greeting}</b>

Я буду напоминать вам о ваших привычках в нужное время.

Для начала работы:
1. Зарегистрируйтесь на сайте
2. Создайте привычки в личном кабинете
3. Я автоматически буду присылать напоминания

Если у вас уже есть аккаунт, просто войдите в него через сайт.

Удачи в формировании полезных привычек!"""

                bot.send_message(chat_id, response_text, parse_mode='HTML')
                return JsonResponse({'ok': True})

            return JsonResponse({'ok': True})

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
