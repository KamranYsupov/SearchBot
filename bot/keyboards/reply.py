from typing import Sequence
from datetime import datetime

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove, KeyboardButtonRequestChat,
)
from django.utils import timezone


def get_reply_keyboard(
    buttons: Sequence[str],
    resize_keyboard: bool = True,
) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=button_text)] for button_text in buttons]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard
    )
    
def get_reply_contact_keyboard(
    text: str = 'Отправить номер телефона 📲'
) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=text, request_contact=True)],
        [KeyboardButton(text='Отмена ❌' )]
    ]
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    

def get_reply_chat_keyboard(
        text: str = 'Выбрать чат'
) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(
            text=text,
            request_chat=KeyboardButtonRequestChat(
                request_id=1,
                chat_is_channel=False,
                request_title=True,
            )
        )],
        [KeyboardButton(text='Отмена ❌')]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_reply_menu_keyboard():
    return get_reply_keyboard(
        buttons=('🔎 Поиск 🔎', '📁 Проекты 📁', )
    )

reply_cancel_keyboard = get_reply_keyboard(buttons=('Отмена ❌',))

reply_keyboard_remove = ReplyKeyboardRemove()

reply_contact_keyboard = get_reply_contact_keyboard()

reply_get_chat_keyboard = get_reply_chat_keyboard()
    
