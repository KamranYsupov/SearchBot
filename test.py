import json

import requests
from aiogram.types import ChatIdUnion
import os

from dotenv import load_dotenv

load_dotenv()

class TelegramService:
    def __init__(
            self,
            bot_token: str = os.getenv('BOT_TOKEN'),
            api_url: str = 'https://api.telegram.org'
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
            reply_to_message_id: int = None,
            parse_mode: str = 'HTML',
    ):
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'reply_to_message_id': reply_to_message_id
        }

        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)

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



tgs = TelegramService()
message = tgs.send_message(
    chat_id=6145206276,
    text='message_to_answer'
).json()
print(message)

# payload = {
#     'chat_id': 6145206276,
#     'text': 'tsfs',
#     'reply_parameters':
#         {'message_id': }
# }
#
# if reply_markup:
#     payload['reply_markup'] = json.dumps(reply_markup)
#
# response = requests.post(
#     url=f'{self.__bot_api_url}/sendMessage',
#     json=payload,
# )


tgs.send_message(
    chat_id=6145206276,
    text='reply_message',
    reply_to_message_id=message['result'].get('message_id')
)


