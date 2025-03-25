from typing import Union, List

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.handlers.state import KeywordState
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import (
    reply_menu_keyboard,
    reply_cancel_keyboard,
)
from bot.utils.pagination import Paginator, get_pagination_buttons
from web.apps.search.models import Chat, Keyword
from web.apps.telegram_users.models import TelegramUser

router = Router()


@router.callback_query(F.data.startswith('kw_l_'))
async def keywords_list_callback_handler(
    callback: types.CallbackQuery,
):
    chat_id, previous_page_number, page_number = callback.data.split('_')[-3:]
    per_page = settings.KEYWORDS_PER_PAGE
    keywords: List[Keyword] = await Keyword.objects.afilter(chat_id=chat_id)
    paginator = Paginator(
        array=keywords,
        page_number=int(page_number),
        per_page=per_page,
    )

    buttons = {
        keyword.text: f'kw_{keyword.id}_{previous_page_number}_{page_number}'
        for keyword in paginator.get_page()
    }

    pagination_buttons = get_pagination_buttons(
        paginator, prefix=f'k_list_{chat_id}_{previous_page_number}'
    )
    sizes = (1,) * per_page

    if not pagination_buttons:
        pass
    elif len(pagination_buttons.items()) == 1:
        sizes += (1, 1)
    else:
        sizes += (2, 1)

    buttons.update(pagination_buttons)
    buttons['Назад 🔙'] = f'chat_{chat_id}_{previous_page_number}'

    await callback.message.edit_text(
        'Выберите ключевое слово.',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=sizes,
        ),
    )


@router.callback_query(F.data.startswith('kw_'))
async def keyword_callback_handler(
        callback: types.CallbackQuery,
):
    (
        keyword_id,
        chats_list_page_number,
        previous_page_number
    ) = callback.data.split('_')[-3:]

    keyword: Keyword = await Keyword.objects.aget(id=keyword_id)

    buttons = {
        'Удалить 🗑': f'ask_rm_kw_{keyword.id}_{chats_list_page_number}_{previous_page_number}',
        'Назад 🔙': \
            f'kw_l_{keyword.chat_id}_{chats_list_page_number}_{previous_page_number}'
    }

    await callback.message.edit_text(
        f'<b>Слово:</b> <em>{keyword.text}</em>',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1, 1,),
        ),
    )


@router.callback_query(F.data.startswith('add_keyword_'))
async def add_keywords_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    chat_id, previous_page_number = callback.data.split('_')[-2:]
    await state.update_data(
        chat_id=chat_id,
        previous_page_number=previous_page_number,
    )

    await callback.message.delete()
    await callback.message.answer(
        'Отправьте ключевое слово 📝',
        reply_markup=reply_cancel_keyboard,
    )
    await state.set_state(KeywordState.text)


@router.message(
    StateFilter(KeywordState.text),
    F.text,
)
async def process_keyword_text_handler(
        message: types.Message,
        state: FSMContext,
):
    if len(message.text) > 150:
        await message.answer('Максимальная длина 150 символов')
        return

    state_data = await state.update_data(text=message.text)
    previous_page_number = state_data.pop('previous_page_number')

    await Keyword.objects.acreate(**state_data)

    await message.answer(
        '<b>Ключевое слово успешно добавлено ✅</b>',
        reply_markup=reply_menu_keyboard
    )

    chat_id = state_data['chat_id']
    await message.answer(
        'Выберите действие.',
        reply_markup=get_inline_keyboard(
            buttons={
                'Назад 🔙': \
                    f'chat_keywords_{chat_id}_{previous_page_number}'
            }
        )
    )


@router.callback_query(F.data.startswith('ask_rm_kw_'))
async def ask_rm_keyword_callback_handler(
        callback: types.CallbackQuery,
):
    (
        keyword_id,
        chats_list_page_number,
        previous_page_number
    ) = callback.data.split('_')[-3:]

    await callback.message.edit_text(
        f'<b>Вы уверены?</b>',
        reply_markup=get_inline_keyboard(
            buttons={
                'Да': f'rm_kw_{keyword_id}_{chats_list_page_number}',
                'Нет': f'kw_{keyword_id}_{chats_list_page_number}_{previous_page_number}'
            }
        ),
    )


@router.callback_query(F.data.startswith('rm_kw_'))
async def rm_keyword_callback_handler(
        callback: types.CallbackQuery,
):
    keyword_id, chats_list_page_number = callback.data.split('_')[-2:]
    keyword = await Keyword.objects.aget(id=keyword_id)
    chat_id = keyword.chat_id

    await keyword.adelete()

    await callback.message.edit_text(
        f'<b>Ключевое слово успешно удалено ✅</b>',
        reply_markup=get_inline_keyboard(
            buttons={'Назад 🔙': f'chat_kws_{chat_id}_{chats_list_page_number}'}
        ),
    )