import json

import requests
from aiogram.types import ChatIdUnion
from django.conf import settings


class TelegramService:
    def __init__(
            self,
            bot_token: str = settings.BOT_TOKEN,
            api_url: str = settings.TELEGRAM_API_URL
    ):
        self.__bot_token = bot_token
        self.api_url = api_url

    @property
    def __bot_api_url(self):
        return f'{self.api_url}/bot{self.__bot_token}'

    def send_message(
            self,
            chat_id: ChatIdUnion,
            text: str,
            reply_markup: dict[str, list] | None = None,
            reply_to: dict[str | int] | None = None,
            parse_mode: str = 'HTML',
    ):
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
        }

        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)

        if reply_to:
            payload['reply_to'] = json.dumps(reply_to)

        response = requests.post(
            url=f'{self.__bot_api_url}/sendMessage',
            json=payload,
        )

        return response

    def forward_message(
            self,
            chat_id: ChatIdUnion,
            from_chat_id: ChatIdUnion,
            message_id: int
    ):
        method = 'forwardMessage'
        url = f'{self.__bot_api_url}/{method}'

        payload = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
        }
        response = requests.post(url=url, json=payload)

        return response


telegram_service = TelegramService()