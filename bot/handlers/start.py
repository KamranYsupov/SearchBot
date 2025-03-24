import loguru
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from django.db.models import Q

from bot.keyboards.reply import reply_menu_keyboard
from web.apps.telegram_users.models import TelegramUser

router = Router()


@router.message(CommandStart())
async def start_command_handler(
    message: types.Message,
):
    from_user = message.from_user
    telegram_user = await TelegramUser.objects.aget(
        Q(telegram_id=from_user.id) |
        Q(username=from_user.username)
    )
    if not telegram_user:
        await message.answer('Отказано в доступе ❌')
        return

    if not telegram_user.full_name:
        telegram_user.telegram_id = from_user.id
        telegram_user.username = from_user.username
        telegram_user.full_name = from_user.full_name
        await telegram_user.asave()

    message_text = f'Привет, {message.from_user.first_name}.'
    await message.answer(
        message_text,
        reply_markup=reply_menu_keyboard,
    )
    
    
    

    
    

