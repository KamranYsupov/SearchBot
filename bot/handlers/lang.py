import loguru
from aiogram import Router, types, F
from asgiref.sync import sync_to_async

from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import get_reply_menu_keyboard
from web.apps.bots.models import BotKeyboard
from web.apps.telegram_users.models import TelegramUser

router = Router()

@router.callback_query(F.data.startswith('lang_'))
async def language_callback_handler(
        callback: types.CallbackQuery,
):
    language = callback.data.split('_')[-1].capitalize()

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    telegram_user.language = language
    await telegram_user.asave()

    texts_model = await telegram_user.get_texts_model()
    message_text = texts_model.choice_language_message_text
    menu_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='menu')

    await callback.message.delete()
    await callback.message.answer(
        message_text,
        reply_markup=await menu_keyboard.as_markup(language=language),
    )