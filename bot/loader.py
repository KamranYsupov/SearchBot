import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()


bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(
        parse_mode='HTML'
    )
)
dp = Dispatcher()