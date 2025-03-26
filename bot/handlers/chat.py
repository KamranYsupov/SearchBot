from typing import Union, List, Sequence, Optional

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings
from pyrogram import Client
from pyrogram.errors import BadRequest, NotAcceptable, UsernameInvalid

from bot.handlers.state import ChatState
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import reply_menu_keyboard, reply_get_chat_keyboard, reply_keyboard_remove, \
    reply_cancel_keyboard
from bot.utils.bot import edit_text_or_answer
from bot.utils.pagination import Paginator, get_pagination_buttons
from web.apps.bots.models import UserBot
from web.apps.search.models import Chat, Keyword
from web.apps.telegram_users.models import TelegramUser

router = Router()

@router.message(
    F.text.lower() == 'отмена ❌'
)
async def cancel_handler(
        message: types.Message,
        state: FSMContext,
):
    await message.answer(
        'Действие отменено',
        reply_markup=reply_menu_keyboard,
    )
    await state.clear()


@router.message(F.text.casefold() == '📁 настройка чатов 📁')
@router.callback_query(F.data == 'chats_settings')
async def chats_settings_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=aiogram_type.from_user.id
    )
    chats = await Chat.objects.afilter(telegram_user_id=telegram_user.id)

    await array_settings_handler(
        aiogram_type,
        list_button_text='Список чатов 🗂',
        callback_prefix='chat',
        array=chats
    )


@router.callback_query(F.data.startswith('chat_kws_'))
async def keywords_settings_handler(
        callback: types.CallbackQuery,
):
    chat_id, previous_page_number = callback.data.split('_')[-2:]
    chat: Chat = await Chat.objects.aget(id=chat_id)

    chat_keywords = await Keyword.objects.afilter(chat_id=chat.id)

    callback_data_end_text = f'{chat.id}_{previous_page_number}'

    await array_settings_handler(
        callback,
        list_button_text='Список ключевых слов 🗂',
        callback_prefix='keyword',
        array=chat_keywords,
        list_button_data=f'kw_l_{chat.id}_{previous_page_number}_1',
        add_button_data=f'add_keyword_{callback_data_end_text}',
        back_button_data=f'chat_{callback_data_end_text}'
    )


async def array_settings_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
        callback_prefix: str,
        list_button_text: str,
        array: Optional[Sequence] = None,
        list_button_data: Optional[str] = None,
        add_button_data: Optional[str] = None,
        back_button_data : Optional[str] = None,
):
    buttons = {}

    if array:
        buttons[list_button_text] = \
            f'{callback_prefix}s_list_1' if not list_button_data else list_button_data

    buttons['Добавить ➕'] = \
        f'add_{callback_prefix}' if not add_button_data else add_button_data

    if back_button_data:
        buttons['Назад 🔙'] = back_button_data

    await edit_text_or_answer(
        aiogram_type,
        text='Выберите действие.',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1)
        )
    )


@router.callback_query(F.data.startswith('chats_list_'))
async def chats_list_callback_handler(
    callback: types.CallbackQuery,
):
    page_number = int(callback.data.split('_')[-1])
    per_page = settings.CHATS_PER_PAGE
    chats: List[Chat] = await Chat.objects.a_all()
    paginator = Paginator(
        array=chats,
        page_number=page_number,
        per_page=per_page,
    )

    buttons = {
        chat.name: f'chat_{chat.id}_{page_number}'
        for chat in paginator.get_page()
    }
    pagination_buttons = get_pagination_buttons(
        paginator, prefix='chats_list'
    )
    sizes = (1,) * per_page

    if not pagination_buttons:
        pass
    elif len(pagination_buttons.items()) == 1:
        sizes += (1, 1)
    else:
        sizes += (2, 1)

    buttons.update(pagination_buttons)
    buttons['Назад 🔙'] = 'chats_settings'

    await callback.message.edit_text(
        'Выберите чат.',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=sizes,
        ),
    )


@router.callback_query(F.data.startswith('chat_'))
async def chat_callback_handler(
        callback: types.CallbackQuery,
):
    chat_id, previous_page_number = callback.data.split('_')[-2:]
    chat: Chat = await Chat.objects.aget(id=chat_id)

    buttons = {
        '💬 Ключевые слова  💬': f'chat_kws_{chat_id}_{previous_page_number}',
        'Удалить 🗑': f'ask_rm_chat_{chat.id}_{previous_page_number}',
        'Назад 🔙': f'chats_list_{previous_page_number}'
    }

    await callback.message.edit_text(
        f'<b>{chat.name}</b>\n\n'
        f'<em>Ссылка: <b>{chat.chat_link}</b></em>',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, 1, 1, ),
        ),
    )

@router.callback_query(F.data.startswith('ask_rm_chat_'))
async def ask_rm_chat_callback_handler(
        callback: types.CallbackQuery,
):
    chat_id, previous_page_number = callback.data.split('_')[-2:]

    await callback.message.edit_text(
        f'<b>Вы уверены?</b>',
        reply_markup=get_inline_keyboard(
            buttons={
                'Да': f'rm_chat_{chat_id}',
                'Нет': f'chat_{chat_id}_{previous_page_number}'
            }
        ),
    )


@router.callback_query(F.data.startswith('rm_chat_'))
async def rm_chat_callback_handler(
        callback: types.CallbackQuery,
):
    chat_id = callback.data.split('_')[-1]
    chat = await Chat.objects.aget(id=chat_id)
    user_bot = await UserBot.objects.aget(id=chat.user_bot_id)
    async with user_bot.configure_client(
            session_workdir=settings.USER_BOTS_SESSIONS_ROOT_2
    ) as client:
        client: Client = client
        try:
            await client.leave_chat(chat.chat_link)
            user_bot.chats_count -= 1
            await user_bot.asave()
        except BadRequest as e:
            pass

    await chat.adelete()


    await callback.message.edit_text(
        f'<b>Чат успешно удален ✅</b>',
        reply_markup=get_inline_keyboard(
            buttons={'Назад 🔙': f'chats_settings'}
        ),
    )


@router.callback_query(F.data == 'add_chat')
async def add_chat_callback_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    await callback.message.delete()
    await callback.message.answer(
        'Отправьте ссылку чата',
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
    chat_exists: bool = await sync_to_async(
        Chat.objects.filter(chat_link=chat_link).exists
    )()

    if chat_exists:
        await message.answer('Этот чат уже добавлен.')
        return

    await state.update_data(chat_link=chat_link)
    await state.set_state(ChatState.name)

    await message.answer('Отправьте название чата 📝')


@router.message(
    StateFilter(ChatState.name),
    F.text,
)
async def process_chat_name_handler(
        message: types.Message,
        state: FSMContext,
):
    if len(message.text) > 100:
        await message.answer('Максимальная длина 100 символов')
        return

    state_data = await state.update_data(name=message.text)
    chat_link = state_data['chat_link']

    user_bot: UserBot = await sync_to_async(
         UserBot.objects.filter(chats_count__lt=500).first
    )()

    async with user_bot.configure_client(
        session_workdir=settings.USER_BOTS_SESSIONS_ROOT_2
    ) as client:
        is_user_bot_chat_member = await sync_to_async(
            Chat.objects.filter(
                chat_link=chat_link,
                user_bot_id=user_bot.id
            ).exists
        )()

        if not is_user_bot_chat_member:
            failure_join_chat = False

            try:
                await client.join_chat(chat_link)
            except UsernameInvalid:
                chat_username = chat_link.split('/')[-1]
                try:
                    await client.join_chat(chat_username)
                except BadRequest:
                    failure_join_chat = True
            except BadRequest:
                failure_join_chat = True

            if failure_join_chat:
                await message.answer(
                    'Не удалось присоединиться к чату.',
                    reply_markup=reply_menu_keyboard,
                )
                await state.clear()
                return

            user_bot.chats_count += 1
            await user_bot.asave()


    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    await Chat.objects.acreate(
        **state_data,
        user_bot_id=user_bot.id,
        telegram_user_id=telegram_user.id
    )

    await message.answer(
        '<b>Чат успешно добавлен ✅</b>',
        reply_markup=reply_menu_keyboard
    )
    await state.clear()



