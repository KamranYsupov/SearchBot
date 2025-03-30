from typing import Union

import loguru
from aiogram import Router, types, F

from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import get_reply_menu_keyboard
from bot.utils.bot import edit_text_or_answer
from web.apps.telegram_users.models import TelegramUser, BotTextsUnion

router = Router()


@router.message(F.text.startswith('🔎 '), F.text.endswith(' 🔎'))
async def search_message_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=aiogram_type.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    button_text = texts_model.turn_on_search_button_text \
        if not telegram_user.search else texts_model.turn_off_search_button_text

    message_data = dict(
        text=texts_model.search_text,
        reply_markup=get_inline_keyboard(
            buttons={button_text: 'change_search_status'},
        )
    )

    await edit_text_or_answer(aiogram_type, **message_data)


@router.callback_query(F.data == 'change_search_status')
async def change_search_callback_handler(
        callback: types.CallbackQuery,
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    telegram_user.search = not telegram_user.search
    await telegram_user.asave()

    await search_message_handler(callback)








