import asyncio
from datetime import timedelta

from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from pyrogram import Client

from web.apps.telegram_users.models import TelegramUser, BotTextsUnion
from web.services.telegram import telegram_service


@shared_task(ignore_result=True)
def send_message_task(
        chat_id: str | int,
        text: str,
):
    telegram_service.send_message(chat_id, text)


@shared_task(ignore_result=True)
def send_ask_message_to_share_bot_task():
    telegram_users = TelegramUser.objects.all()

    for telegram_user in telegram_users:
        texts_model: BotTextsUnion = async_to_sync(
            telegram_user.get_texts_model
        )()

        send_message_task.delay(
            telegram_user.telegram_id,
            texts_model.share_request_text
        )

