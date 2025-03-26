import asyncio
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from pyrogram import Client

from web.apps.telegram_users.models import TelegramUser
from web.services.telegram import telegram_service


@shared_task(ignore_result=True)
def send_message_task(
        chat_id: str | int,
        text: str,
):
    telegram_service.send_message(chat_id, text)


@shared_task(ignore_result=True)
def send_ask_message_to_share_bot_task(
    text: str = 'Нравиться наш бот? Поделитесь с друзьями!',
):
    chat_ids = TelegramUser.objects.all().values_list(
        'telegram_id', flat=True
    )

    for chat_id in chat_ids:
        send_message_task.delay(chat_id, text)

