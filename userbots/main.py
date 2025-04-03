import os
from typing import List

import django
import loguru
from pyrogram import utils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.core.settings')
django.setup()

from web.apps.bots.models import UserBot
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from userbots.handlers import handle_groups
from bot.container import Container
from userbots.utils.peer import get_peer_type_new


def main():
    """
    Функция для запуска telethon юзерботов,
    скорее всего для каждого нового юзербота потребуется
    создавать новый docker контейнер, т. к. telethon
    не позволяет запускать бота в фоновом режиме без блокировки остальной части программы.
    ИЛИ рассмотреть вариант с asyncio.gather()

    ПРЕДПОЧТИТЕЛЬНЕЙ будет вариант с новым контейнером
    """
    utils.get_peer_type = get_peer_type_new

    user_bots: List[UserBot] = UserBot.objects.all()

    clients = [
        TelegramClient(
            session=StringSession(user_bot.telethon_session_string),
            api_id=user_bot.api_id,
            api_hash=user_bot.api_hash,
        )
        for user_bot in user_bots
    ]

    client = clients[0]

    client.add_event_handler(handle_groups, events.NewMessage())

    client.start()
    client.run_until_disconnected()


if __name__ == '__main__':
    loguru.logger.info('UserBot is starting')

    container = Container()
    container.init_resources()
    container.wire(modules=[__name__, 'handlers',])

    main()