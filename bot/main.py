﻿import asyncio
import os

import django
from django.conf import settings
import loguru
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from pyrogram import utils


async def main():
    """Запуск бота"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.core.settings')

    django.setup()

    from middlewares.throttling import rate_limit_middleware
    from handlers.routing import get_main_router
    from userbots.utils.peer import get_peer_type_new
    from bot.loader import bot, dp
    from bot.handlers.lead_chat import router as lead_chat_router

    utils.get_peer_type = get_peer_type_new


    try:
        dp.include_routers(get_main_router(), lead_chat_router)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    loguru.logger.info('Bot is starting')
    asyncio.run(main())
