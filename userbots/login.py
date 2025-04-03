import asyncio
import os

import django
import loguru
from asgiref.sync import sync_to_async
from pyrogram import Client
from telethon import TelegramClient
from telethon.sessions import StringSession

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.core.settings')
django.setup()

from web.apps.bots.models import UserBot

async def login(
        name: str,
        api_id: int | str,
        api_hash: str,
        phone_number: str,
):
    """Функция для авторизауии и создания в БД юзерботов"""
    async with Client(
        name=name,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number,
    ) as client:
        pyrogram_session_string = await client.export_session_string()

    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        telethon_session_string = client.session.save()

    await sync_to_async(UserBot.objects.update_or_create)(
        name=name,
        defaults=dict(
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
            pyrogram_session_string=pyrogram_session_string,
            telethon_session_string=telethon_session_string
        )
    )

    loguru.logger.info('Юзербот успешно создан!')


if __name__ == '__main__':
    name = input('Введите username: ')
    api_id = input('Введите api_id: ')
    api_hash = input('Введите api_hash: ')
    phone_number = input('Введите номер телефона: ')

    asyncio.run(
        login(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
        )
    )


