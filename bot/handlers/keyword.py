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
    get_reply_menu_keyboard,
    reply_cancel_keyboard, reply_get_chat_keyboard,
)
from web.apps.bots.models import BotKeyboard
from web.apps.search.models import Keyword
from web.apps.telegram_users.models import TelegramUser, BotTextsUnion

router = Router()


@router.callback_query(F.data.startswith('p_kws_'))
async def project_keywords_settings_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    keywords = await Keyword.objects.afilter(project_id=project_id)

    handler_callback_data = f'{project_id}_{previous_page_number}'

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await array_settings_handler(
        callback,
        list_button_text=texts_model.keywords_list_button_text,
        callback_prefix='keyword',
        array=keywords,
        list_button_data=f'kws_l_{handler_callback_data}_1',
        add_button_data=f'add_kw_{handler_callback_data}',
        back_button_data=f'project_{handler_callback_data}',
        message_text=texts_model.choice_action_text,
        add_button_text=texts_model.add_button_text,
        back_button_text=texts_model.back_button_text,
    )


@router.callback_query(F.data.startswith('kws_l_'))
async def keywords_list_callback_handler(
    callback: types.CallbackQuery,
):
    project_id = callback.data.split('_')[-3]
    previous_page_number, page_number = map(int, callback.data.split('_')[-2:])

    keywords: List[Keyword] = await Keyword.objects.afilter(project_id=project_id)
    pagination_callback_data = f'{project_id}_{previous_page_number}'

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await list_handler(
        callback,
        callback_prefix=f'keyword_{previous_page_number}',
        array=keywords,
        button_text_obj_attr_name='text',
        page_number=page_number,
        per_page=settings.KEYWORDS_PER_PAGE,
        message_text=texts_model.keywords_list_text,
        back_button_text=texts_model.back_button_text,
        back_button_callback_data=f'p_kws_{pagination_callback_data}',
        pagination_buttons_prefix=f'kws_l_{pagination_callback_data}'
    )


@router.callback_query(F.data.startswith('keyword_'))
async def keyword_callback_handler(
        callback: types.CallbackQuery,
):
    previous_page_number, keyword_id, page_number = callback.data.split('_')[-3:]
    keyword: Keyword = await Keyword.objects.aget(id=keyword_id)
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {
        texts_model.delete_button_text:
            f'ask_rm_kw_{keyword.id}_{previous_page_number}_{page_number}',
        texts_model.back_button_text:
            f'kws_l_{keyword.project_id}_{previous_page_number}_{page_number}',
    }

    await callback.message.edit_text(
        texts_model.keyword_text.format(
            keyword=keyword.text
        ),
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1, ),
        ),
    )


@router.callback_query(F.data.startswith('ask_rm_kw_'))
async def ask_rm_keyword_callback_handler(
        callback: types.CallbackQuery,
):
    keyword_id, previous_page_number, page_number = callback.data.split('_')[-3:]
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {
        texts_model.yes_button_text:
            f'rm_kw_{keyword_id}_{previous_page_number}_{page_number}',
        texts_model.no_button_text:
            f'keyword_{previous_page_number}_{keyword_id}_{page_number}'
    }

    await callback.message.edit_text(
        texts_model.sure_text,
        reply_markup=get_inline_keyboard(buttons=buttons),
    )


@router.callback_query(F.data.startswith('rm_kw_'))
async def rm_keyword_callback_handler(
        callback: types.CallbackQuery,
):
    keyword_id, previous_page_number, page_number = callback.data.split('_')[-3:]
    keyword: Keyword = await Keyword.objects.aget(id=keyword_id)
    project_id = keyword.project_id

    await keyword.adelete()
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    success_text = texts_model.successful_rm_keyword_text
    await callback.message.edit_text(
        text=success_text,
        reply_markup=get_inline_keyboard(
            buttons={
                texts_model.back_button_text:
                    f'project_{project_id}_{previous_page_number}'
            }
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
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await callback.message.delete()
    await callback.message.answer(
        texts_model.ask_send_keyword_text,
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
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    keyword_text_max_length = 150
    keywords = message.text.split(',')

    for keyword in keywords:
        if len(keyword) > keyword_text_max_length:
            await message.answer(
                texts_model.keyword_max_length_error_text.format(
                    max_length=keyword_text_max_length
                )
            )
            return

    state_data = await state.get_data()
    project_id = state_data['project_id']


    existing_keywords = await sync_to_async(list)(
        await sync_to_async(
            Keyword.objects.filter(
                text__in=keywords,
                project_id=project_id
            ).values_list
        )('text', flat=True)
    )

    if existing_keywords and len(keywords) == 1:
        await message.answer(
            texts_model.keyword_exists_error_text.format(keyword=message.text)
        )
        return
    else:
        unique_keywords = []

        for keyword in keywords:
            if keyword not in existing_keywords:
                unique_keywords.append(
                    Keyword(text=keyword, project_id=project_id)
                )
                continue

            await message.answer(
                texts_model.keyword_exists_error_text.format(keyword=message.text)
            )
            return


    await sync_to_async(Keyword.objects.bulk_create)(unique_keywords)

    menu_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='menu')

    await message.answer(
        texts_model.successful_add_keyword_text,
        reply_markup=await menu_keyboard.as_markup(language=telegram_user.language)
    )
    previous_page_number = state_data['previous_page_number']

    await state.clear()
    await message.answer(
        texts_model.choice_action_text,
        reply_markup=get_inline_keyboard(
            buttons={
                texts_model.back_button_text: \
                    f'p_kws_{project_id}_{previous_page_number}'
            }
        )
    )


