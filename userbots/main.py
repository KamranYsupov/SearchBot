import asyncio
import os
from typing import List

import django
import loguru
from pyrogram import Client


def main():
    """Запуск юзер ботов"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.core.settings')

    django.setup()
    from web.apps.bots.models import UserBot
    from userbots.handlers import message_handler

    clients: List[Client] = [user_bot.configure_client() for user_bot in UserBot.objects.all()]

    for client in clients:
        client.add_handler(message_handler)
        client.run()


if __name__ == '__main__':
    loguru.logger.info('User bots are starting')
    main()
