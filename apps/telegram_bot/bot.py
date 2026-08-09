import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    BASE_URL = 'https://api.telegram.org/bot'

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"{self.BASE_URL}{self.token}/"

    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Send message to Telegram user"""
        url = f"{self.base_url}sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Telegram message: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return None

    def set_webhook(self, webhook_url):
        """Set webhook for bot"""
        url = f"{self.base_url}setWebhook"
        payload = {'url': webhook_url}

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error setting webhook: {e}")
            return None

    def delete_webhook(self):
        """Delete webhook"""
        url = f"{self.base_url}deleteWebhook"

        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting webhook: {e}")
            return None


bot = TelegramBot()
