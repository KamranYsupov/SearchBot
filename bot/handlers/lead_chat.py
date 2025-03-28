from typing import Union, List, Sequence, Optional

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Q
from pyrogram import Client
from pyrogram.types import ChatPreview

from bot.handlers.state import LeadChatState
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import reply_menu_keyboard, reply_keyboard_remove, \
    reply_cancel_keyboard, reply_get_chat_keyboard
from web.apps.bots.models import UserBot
from web.apps.search.models import Chat, Keyword, Project, Match
from web.apps.telegram_users.models import TelegramUser

router = Router()


@router.callback_query(F.data.startswith('lead_chat_'))
async def lead_chat_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    project: Project = await Project.objects.aget(id=project_id)

    buttons = {}
    buttons_callback_data = f'{project.id}_{previous_page_number}'

    if not project.lead_chat_id:
        text = 'Выберите действие.'
        buttons['Добавить ➕'] = f'add_l_c_{buttons_callback_data}'
    else:
        text = f'<b>{project.lead_chat_name}</b>'
        buttons['Удалить 🗑'] = f'ask_rm_l_c_{buttons_callback_data}'

    buttons['Назад 🔙'] = f'project_{buttons_callback_data}'

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

    await callback.message.delete()
    text = 'Выберите чат.'
    await callback.message.answer(
        text,
        reply_markup=reply_get_chat_keyboard,
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
    if await sync_to_async(
        Project.objects.filter(
            Q(lead_chat_id=chat_id),
            ~Q(telegram_user_id=message.from_user.id),
        ).exists
    )():
        lead_chat_exists_text = 'Этот чат уже добавлен другим пользователем.'
        await message.answer(lead_chat_exists_text)
        await state.clear()
        return

    state_data = await state.get_data()
    project_id = state_data['project_id']
    previous_page_number = state_data['previous_page_number']

    await sync_to_async(Project.objects.filter(id=project_id).update)(
        lead_chat_id=chat_id,
        lead_chat_name=message.chat_shared.title
    )

    success_text = (
        '<b>Группа успешно добавлена ✅.</b>\n\n'
        '<em>Не забудьте добавить бота в группу для получения совпадений.</em>'
    )
    await message.answer(
        success_text,
        reply_markup=reply_menu_keyboard,
    )
    await state.clear()

    choice_action_text = 'Выберите действие.'
    back_button_text = 'Назад 🔙'
    buttons = {back_button_text: f'project_{project_id}_{previous_page_number}'}

    await message.answer(
        choice_action_text,
        reply_markup=get_inline_keyboard(buttons=buttons)
    )


@router.callback_query(F.data.startswith('ask_rm_l_c_'))
async def ask_rm_lead_chat_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    buttons_callback_data = f'{project_id}_{previous_page_number}'

    buttons = {
        'Да': f'rm_l_c_{buttons_callback_data}',
        'Нет': f'lead_chat_{buttons_callback_data}'
    }

    await callback.message.edit_text(
        f'<b>Вы уверены?</b>',
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

    success_text = '<b>Группа успешно удаленна ✅</b>'
    back_button_text = 'Назад 🔙'

    await callback.message.edit_text(
        text=success_text,
        reply_markup=get_inline_keyboard(
            buttons={back_button_text: f'project_{project_id}_{previous_page_number}'}
        ),
    )


@router.message(F.chat.id == int(settings.KEYWORDS_MATCHES_BUFFER_GROUP_ID))
async def send_match_from_buffer_group_handler(
        message: types.Message,
):
    match: Match = await sync_to_async(
        Match.objects.select_related(
            'chat',
            'keyword',
            'keyword__project__telegram_user'
        ).filter(message_id=message.message_id).first
    )()
    if not match:
        return

    lead_chat_id = match.keyword.project.lead_chat_id

    forwarded_message = await message.forward(chat_id=lead_chat_id)

    message_template = (
        'Найдено совпадение слова <em>{keyword}</em> '
        'в чате <b>{chat}</b>!\n\n'

        + (f'<b>Автор</b>: @{match.from_user_username}\n\n'
        if match.from_user_username else '')

        + ('<a href="{message_link}">'
        '<b><em>Ссылка на сообщение</em></b>'
        '</a>' if not match.chat.is_private else '')
    )
    message_text = message_template.format(
        keyword=match.keyword.text,
        chat=match.chat.name,
        message_link=match.message_link,
    )

    await message.bot.send_message(
        chat_id=lead_chat_id,
        text=message_text,
        reply_to_message_id=forwarded_message.message_id,
    )





