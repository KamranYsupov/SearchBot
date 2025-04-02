import asyncio
import os
from typing import List

import django
import loguru
from pyrogram import Client, utils

from dependency_injector.wiring import inject, Provide


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.core.settings')
django.setup()

from bot.container import Container


@inject
async def main(
    client_1: Client = Provide[Container.client_1],
):
    """Запуск юзер ботов"""
    from middlewares.throttling import rate_limit_middleware
    from handlers.routing import get_main_router
    from userbots.utils.peer import get_peer_type_new
    from userbots.handlers import message_handler
    from bot.loader import bot, dp


    utils.get_peer_type = get_peer_type_new

    dp.message.middleware(rate_limit_middleware)
    dp.include_routers(get_main_router())

    clients = [client_1]

    try:
        for client in clients:
            client.add_handler(message_handler)
            await client.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        for client in clients:
            await client.stop()
        await bot.session.close()


if __name__ == '__main__':
    loguru.logger.info('Bot is starting')
    container = Container()
    container.init_resources()
    container.wire(
        modules=[
            __name__,
            'handlers.chat',
            'handlers.project',
        ]
    )
    asyncio.run(main())

