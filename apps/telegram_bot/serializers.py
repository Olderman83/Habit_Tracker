from rest_framework import serializers


class TelegramMessageSerializer(serializers.Serializer):
    """Схема для входящего сообщения от Telegram"""
    message_id = serializers.IntegerField()
    from_user = serializers.DictField(source='from')
    chat = serializers.DictField()
    date = serializers.IntegerField()
    text = serializers.CharField(required=False, allow_blank=True)


class TelegramUpdateSerializer(serializers.Serializer):
    """Схема для обновления от Telegram"""
    update_id = serializers.IntegerField()
    message = TelegramMessageSerializer(required=False)
