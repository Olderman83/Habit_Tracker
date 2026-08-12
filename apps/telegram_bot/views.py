import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import serializers
from .bot import bot

logger = logging.getLogger(__name__)


# Определяем схемы для документации
class TelegramMessageSerializer(serializers.Serializer):
    """Схема для входящего сообщения от Telegram"""

    message_id = serializers.IntegerField()
    from_user = serializers.DictField(source="from")
    chat = serializers.DictField()
    date = serializers.IntegerField()
    text = serializers.CharField(required=False)


class TelegramUpdateSerializer(serializers.Serializer):
    """Схема для обновления от Telegram"""

    update_id = serializers.IntegerField()
    message = TelegramMessageSerializer(required=False)


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(APIView):
    """Обработка обновлений вебхука Telegram"""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Telegram Webhook",
        description="""
            Эндпоинт для получения обновлений от Telegram.

            Поддерживаемые команды:
            - `/start` - приветственное сообщение с инструкцией

            Webhook должен быть настроен в Telegram Bot API.
            """,
        request=TelegramUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Webhook успешно обработан",
                response={
                    "type": "object",
                    "properties": {"ok": {"type": "boolean", "example": True}},
                },
            ),
            500: OpenApiResponse(
                description="Ошибка обработки webhook",
                response={
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean", "example": False},
                        "error": {"type": "string", "example": "Error description"},
                    },
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Пример команды /start",
                value={
                    "update_id": 123456789,
                    "message": {
                        "message_id": 1,
                        "from": {"id": 123456789, "username": "telegram_user"},
                        "chat": {"id": 123456789},
                        "date": 1234567890,
                        "text": "/start",
                    },
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример обычного сообщения",
                value={
                    "update_id": 123456789,
                    "message": {
                        "message_id": 1,
                        "from": {"id": 123456789, "username": "telegram_user"},
                        "chat": {"id": 123456789},
                        "date": 1234567890,
                        "text": "Hello",
                    },
                },
                request_only=True,
            ),
            OpenApiExample("Успешный ответ", value={"ok": True}, response_only=True),
            OpenApiExample(
                "Ответ с ошибкой",
                value={"ok": False, "error": "Invalid request format"},
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            data = request.data
            logger.info(f"Received webhook: {data}")

            if "message" in data and data["message"].get("text") == "/start":
                chat_id = data["message"]["chat"]["id"]

                response_text = """👋 <b>Добро пожаловать в Трекер Привычек!</b>

Я буду напоминать вам о ваших привычках в нужное время.

Для начала работы:
1. Зарегистрируйтесь на сайте
2. Создайте привычки в личном кабинете
3. Я автоматически буду присылать напоминания

Если у вас уже есть аккаунт, просто войдите в него через сайт.

Удачи в формировании полезных привычек!"""

                bot.send_message(chat_id, response_text, parse_mode="HTML")
                return JsonResponse({"ok": True})

            return JsonResponse({"ok": True})

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({"ok": False, "error": str(e)}, status=500)
