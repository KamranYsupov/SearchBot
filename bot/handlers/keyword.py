from typing import Union, List

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Q

from bot.handlers.state import KeywordState
from bot.handlers.utils import array_settings_handler, list_handler
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import (
    reply_menu_keyboard,
    reply_cancel_keyboard, reply_get_chat_keyboard,
)
from web.apps.search.models import Keyword

router = Router()


@router.callback_query(F.data.startswith('p_kws_'))
async def project_keywords_settings_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    keywords = await Keyword.objects.afilter(project_id=project_id)

    handler_callback_data = f'{project_id}_{previous_page_number}'

    await array_settings_handler(
        callback,
        list_button_text='Список ключевых слов 🗂',
        callback_prefix='keyword',
        array=keywords,
        list_button_data=f'kws_l_{handler_callback_data}_1',
        add_button_data=f'add_kw_{handler_callback_data}',
        back_button_data=f'project_{handler_callback_data}'
    )


@router.callback_query(F.data.startswith('kws_l_'))
async def keywords_list_callback_handler(
    callback: types.CallbackQuery,
):
    project_id = callback.data.split('_')[-3]
    previous_page_number, page_number = map(int, callback.data.split('_')[-2:])

    keywords: List[Keyword] = await Keyword.objects.afilter(project_id=project_id)
    pagination_callback_data = f'{project_id}_{previous_page_number}'
    await list_handler(
        callback,
        callback_prefix=f'keyword_{previous_page_number}',
        array=keywords,
        button_text_obj_attr_name='text',
        page_number=page_number,
        per_page=settings.KEYWORDS_PER_PAGE,
        message_text='Выберите ключевое слово.',
        back_button_callback_data=f'p_kws_{pagination_callback_data}',
        pagination_buttons_prefix=f'kw_l_{pagination_callback_data}_{page_number}'
    )


@router.callback_query(F.data.startswith('keyword_'))
async def keyword_callback_handler(
        callback: types.CallbackQuery,
):
    previous_page_number, keyword_id, page_number = callback.data.split('_')[-3:]
    keyword: Keyword = await Keyword.objects.aget(id=keyword_id)

    buttons = {
        'Удалить 🗑': f'ask_rm_kw_{keyword.id}_{previous_page_number}_{page_number}',
        'Назад 🔙': \
            f'kws_l_{keyword.project_id}_{previous_page_number}_{page_number}'
    }

    await callback.message.edit_text(
        f'<b>Слово:</b> <em>{keyword.text}</em>',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1),
        ),
    )


@router.callback_query(F.data.startswith('ask_rm_kw_'))
async def ask_rm_keyword_callback_handler(
        callback: types.CallbackQuery,
):
    keyword_id, previous_page_number, page_number = callback.data.split('_')[-3:]

    await callback.message.edit_text(
        f'<b>Вы уверены?</b>',
        reply_markup=get_inline_keyboard(
            buttons={
                'Да': f'rm_kw_{keyword_id}_{previous_page_number}_{page_number}',
                'Нет': f'keyword_{previous_page_number}_{keyword_id}_{page_number}'
            }
        ),
    )


@router.callback_query(F.data.startswith('rm_kw_'))
async def rm_keyword_callback_handler(
        callback: types.CallbackQuery,
):
    keyword_id, previous_page_number, page_number = callback.data.split('_')[-3:]
    keyword: Keyword = await Keyword.objects.aget(id=keyword_id)
    project_id = keyword.project_id

    await keyword.adelete()

    success_text = '<b>Ключевое слово успешно удалено ✅</b>'
    back_button_text = 'Назад 🔙'
    await callback.message.edit_text(
        text=success_text,
        reply_markup=get_inline_keyboard(
            buttons={back_button_text: f'project_{project_id}_{previous_page_number}'}
        ),
    )


@router.callback_query(F.data.startswith('add_kw_'))
async def add_keywords_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    await state.update_data(
        project_id=project_id,
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
    keyword_text_max_length = 150
    if len(message.text) > keyword_text_max_length:
        await message.answer(
            f'Максимальная длина {keyword_text_max_length} символов'
        )
        return

    state_data = await state.get_data()
    project_id = state_data['project_id']

    keyword_exists = await sync_to_async(
        Keyword.objects.filter(
            text=message.text,
            project_id=project_id
        ).exists
    )()
    if keyword_exists:
        await message.answer(
            'В данный проект уже добавлено '
            f'ключевое слово "{message.text}"'
        )
        return

    await Keyword.objects.acreate(
        text=message.text,
        project_id=project_id
    )

    await message.answer(
        '<b>Ключевое слово успешно добавлено ✅</b>',
        reply_markup=reply_menu_keyboard
    )
    await state.clear()

    previous_page_number = state_data['previous_page_number']
    await message.answer(
        'Выберите действие.',
        reply_markup=get_inline_keyboard(
            buttons={
                'Назад 🔙': \
                    f'p_kws_{project_id}_{previous_page_number}'
            }
        )
    )

