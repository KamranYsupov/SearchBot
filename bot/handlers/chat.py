import uuid
from typing import Union, List, Sequence, Optional

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import BadRequest, NotAcceptable, UsernameInvalid

from bot.handlers.state import ChatState
from bot.handlers.utils import array_settings_handler, list_handler
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import get_reply_menu_keyboard, reply_get_chat_keyboard, reply_keyboard_remove, \
    reply_cancel_keyboard
from bot.utils.bot import edit_text_or_answer
from bot.utils.pagination import Paginator, get_pagination_buttons
from bot.utils.userbot import join_chat, leave_chat
from web.apps.bots.models import UserBot, BotKeyboard
from web.apps.search.models import Chat, Keyword
from web.apps.telegram_users.models import TelegramUser, BotTextsUnion

router = Router()


@router.callback_query(F.data.startswith('p_chats_'))
async def project_chats_settings_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    chats = await Chat.objects.afilter(project_id=project_id)

    handler_callback_data = f'{project_id}_{previous_page_number}'

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await array_settings_handler(
        callback,
        list_button_text=texts_model.chats_list_button_text,
        callback_prefix='chat',
        array=chats,
        list_button_data=f'chats_l_{handler_callback_data}_1',
        add_button_data=f'add_chat_{handler_callback_data}',
        back_button_data=f'project_{handler_callback_data}',
        message_text=texts_model.choice_action_text,
        add_button_text=texts_model.add_button_text,
        back_button_text=texts_model.back_button_text,
    )


@router.callback_query(F.data.startswith('chats_l_'))
async def chats_list_callback_handler(
    callback: types.CallbackQuery,
):
    project_id = callback.data.split('_')[-3]
    previous_page_number, page_number = map(int, callback.data.split('_')[-2:])

    chats: List[Chat] = await Chat.objects.afilter(project_id=project_id)
    pagination_callback_data = f'{project_id}_{previous_page_number}'

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await list_handler(
        callback,
        callback_prefix=f'chat_{previous_page_number}',
        array=chats,
        button_text_obj_attr_name='name',
        page_number=page_number,
        per_page=settings.CHATS_PER_PAGE,
        message_text=texts_model.chats_list_text,
        back_button_text=texts_model.back_button_text,
        back_button_callback_data=f'p_chats_{pagination_callback_data}',
        pagination_buttons_prefix=f'chats_l_{pagination_callback_data}',
    )


@router.callback_query(F.data.startswith('chat_'))
async def chat_callback_handler(
        callback: types.CallbackQuery,
):
    previous_page_number, chat_id, page_number = callback.data.split('_')[-3:]
    chat: Chat = await Chat.objects.aget(id=chat_id)

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {
        texts_model.delete_button_text: f'ask_rm_chat_{chat.id}_{previous_page_number}_{page_number}',
        texts_model.back_button_text: f'chats_l_{chat.project_id}_{previous_page_number}_{page_number}'
    }

    await callback.message.edit_text(
        texts_model.chat_text.format(
            chat_name=chat.name,
            chat_link=chat.chat_link,
        ),
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1, 1, ),
        ),
    )

@router.callback_query(F.data.startswith('ask_rm_chat_'))
async def ask_rm_chat_callback_handler(
        callback: types.CallbackQuery,
):
    chat_id, previous_page_number, page_number = callback.data.split('_')[-3:]
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {
        texts_model.yes_button_text:
            f'rm_chat_{chat_id}_{previous_page_number}_{page_number}',
        texts_model.no_button_text:
            f'chat_{previous_page_number}_{chat_id}_{page_number}'
    }
    await callback.message.edit_text(
        texts_model.sure_text,
        reply_markup=get_inline_keyboard(buttons=buttons),
    )


@router.callback_query(F.data.startswith('rm_chat_'))
async def rm_chat_callback_handler(
        callback: types.CallbackQuery,
):
    chat_id, previous_page_number, page_number = callback.data.split('_')[-3:]
    chat: Chat = await Chat.objects.aget(id=chat_id)
    project_id = chat.project_id

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await callback.message.edit_text(texts_model.wait_text)

    user_bot = await UserBot.objects.aget(id=chat.user_bot_id)
    await leave_chat(chat.chat_id, user_bot)
    await chat.adelete()

    await callback.message.edit_text(
        texts_model.successful_rm_chat_text,
        reply_markup=get_inline_keyboard(
            buttons={
                texts_model.back_button_text:
                    f'project_{project_id}_{previous_page_number}'
            }
        ),
    )


@router.callback_query(F.data.startswith('add_chat_'))
async def add_chat_callback_handler(
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
        texts_model.ask_send_chat_link_text,
        reply_markup=reply_cancel_keyboard,
    )
    await state.set_state(ChatState.chat_link)


@router.message(
    StateFilter(ChatState.chat_link),
    F.text,
)
async def process_chat_link_handler(
        message: types.Message,
        state: FSMContext,
):
    chat_link = message.text
    state_data = await state.update_data(chat_link=chat_link)
    chat_exists: bool = await sync_to_async(
        Chat.objects.filter(
            chat_link=chat_link,
            project_id=state_data['project_id']
        ).exists
    )()
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()
    menu_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='menu')

    if chat_exists:
        await message.answer(texts_model.chat_exists_error_text)
        return

    wait_message = await message.answer(texts_model.wait_text)

    user_bot: UserBot = await sync_to_async(
        UserBot.objects.filter(chats_count__lt=500).first
    )()
    pyrogram_chat, is_private = await join_chat(
        chat_link=chat_link,
        user_bot=user_bot,
        return_is_private=True,
    )

    if not pyrogram_chat:
        await message.answer(
            texts_model.join_chat_error_text,
            reply_markup=await menu_keyboard.as_markup(language=telegram_user.language),
        )
        await message.bot.delete_message(
            message.from_user.id,
            message_id=wait_message.message_id
        )
        await state.clear()
        return

    state_data = await state.update_data(
        chat_id=pyrogram_chat.id,
        name=pyrogram_chat.title,
        is_private=is_private,
    )
    project_id = state_data['project_id']
    previous_page_number = state_data.pop('previous_page_number')

    await Chat.objects.acreate(
        **state_data,
        user_bot_id=user_bot.id,
    )
    await state.clear()


    await message.bot.delete_message(
        message.from_user.id,
        message_id=wait_message.message_id
    )
    await message.answer(
        texts_model.successful_add_chat_text,
        reply_markup=await menu_keyboard.as_markup(language=telegram_user.language)
    )

    await message.answer(
        texts_model.choice_action_text,
        reply_markup=get_inline_keyboard(
            buttons={
                texts_model.back_button_text: \
                    f'p_chats_{project_id}_{previous_page_number}'
            }
        )
    )






