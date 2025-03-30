from typing import Union, List, Sequence, Optional

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestChat
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Q
from pyrogram import Client
from pyrogram.types import ChatPreview

from bot.handlers.state import LeadChatState
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import get_reply_menu_keyboard, reply_keyboard_remove, \
    reply_cancel_keyboard, reply_get_chat_keyboard
from web.apps.bots.models import UserBot, BotKeyboard
from web.apps.search.models import Chat, Keyword, Project, Match
from web.apps.telegram_users.models import TelegramUser, BotTextsUnion
from web.db.model_mixins import LanguageMixin

router = Router()


@router.callback_query(F.data.startswith('lead_chat_'))
async def lead_chat_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    project: Project = await Project.objects.aget(id=project_id)

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {}
    buttons_callback_data = f'{project.id}_{previous_page_number}'


    if not project.lead_chat_id:
        text = texts_model.choice_action_text
        buttons[texts_model.add_button_text] = f'add_l_c_{buttons_callback_data}'
    else:
        text = f'<b>{project.lead_chat_name}</b>'
        buttons[texts_model.delete_button_text] = f'ask_rm_l_c_{buttons_callback_data}'

    buttons[texts_model.back_button_text] = f'project_{buttons_callback_data}'

    await callback.message.edit_text(
        text,
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1)
        )
    )


@router.callback_query(F.data.startswith('add_l_c_'))
async def add_lead_chat_handler(
        callback: types.CallbackQuery,
        state: FSMContext
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    await state.update_data(
        project_id=project_id,
        previous_page_number=previous_page_number,
    )
    await state.set_state(LeadChatState.chat_id)

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()
    request_chat_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='request_chat')

    text_field_name = request_chat_keyboard.get_text_name(telegram_user.language)
    buttons = await sync_to_async(list)(
        await sync_to_async(
            request_chat_keyboard.buttons
            .all()
            .values_list
        )(text_field_name, flat=True)
    )
    keyboard = [
        [KeyboardButton(
            text=buttons[0],
            request_chat=KeyboardButtonRequestChat(
                request_id=1,
                chat_is_channel=False,
                request_title=True,
            ))
        ],
        [KeyboardButton(text=buttons[1])]
    ]

    await callback.message.delete()
    await callback.message.answer(
        texts_model.chats_list_text,
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True),
    )


@router.message(
    F.chat_shared,
    StateFilter(LeadChatState.chat_id)
)
async def process_chat_id_handler(
        message: types.Message,
        state: FSMContext,
):
    chat_id = message.chat_shared.chat_id
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    if await sync_to_async(
        Project.objects.filter(
            Q(lead_chat_id=chat_id),
            ~Q(telegram_user_id=message.from_user.id),
        ).exists
    )():
        await message.answer(texts_model.lead_chat_exists_error_text)
        await state.clear()
        return

    state_data = await state.get_data()
    project_id = state_data['project_id']
    previous_page_number = state_data['previous_page_number']

    await sync_to_async(Project.objects.filter(id=project_id).update)(
        lead_chat_id=chat_id,
        lead_chat_name=message.chat_shared.title
    )
    menu_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='menu')

    await message.answer(
        texts_model.successful_add_lead_chat_text,
        reply_markup=await menu_keyboard.as_markup(language=telegram_user.language),
    )
    await state.clear()

    buttons = {
        texts_model.back_button_text:
            f'project_{project_id}_{previous_page_number}'
    }

    await message.answer(
        texts_model.choice_action_text,
        reply_markup=get_inline_keyboard(buttons=buttons)
    )


@router.callback_query(F.data.startswith('ask_rm_l_c_'))
async def ask_rm_lead_chat_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    buttons_callback_data = f'{project_id}_{previous_page_number}'

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {
        texts_model.yes_button_text: f'rm_l_c_{buttons_callback_data}',
        texts_model.no_button_text: f'lead_chat_{buttons_callback_data}'
    }

    await callback.message.edit_text(
        texts_model.sure_text,
        reply_markup=get_inline_keyboard(
            buttons=buttons
        ),
    )


@router.callback_query(F.data.startswith('rm_l_c_'))
async def rm_lead_chat_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]

    await sync_to_async(Project.objects.filter(id=project_id).update)(
        lead_chat_id=None,
        lead_chat_name=None
    )

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await callback.message.edit_text(
        texts_model.successful_rm_lead_chat_text,
        reply_markup=get_inline_keyboard(
            buttons={
                texts_model.back_button_text:
                    f'project_{project_id}_{previous_page_number}'
            }
        ),
    )




