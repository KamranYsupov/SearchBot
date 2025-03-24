from typing import Union, List

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from bot.handlers.state import ChatState
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import reply_menu_keyboard, reply_get_chat_keyboard, reply_keyboard_remove
from bot.utils.bot import edit_text_or_answer
from bot.utils.pagination import Paginator, get_pagination_buttons
from web.apps.search.models import Chat
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
async def chat_settings_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=aiogram_type.from_user.id
    )
    buttons = {}

    if await sync_to_async(telegram_user.chats.exists)():
        buttons['Список чатов 🗂'] = 'chats_list_1'

    buttons['Добавить ➕'] = 'add_chat'

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
    per_page = 3
    products: List[Chat] = await Chat.objects.a_all()
    paginator = Paginator(
        array=products,
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
    await callback.message.edit_text(
        f'<b>{chat.name}</b>',
        reply_markup=get_inline_keyboard(
            buttons={
                'Удалить 🗑': f'ask_rm_chat_{chat.id}_{previous_page_number}',
                'Назад 🔙': f'chats_list_{previous_page_number}'
            }
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
    await sync_to_async(Chat.objects.filter(id=chat_id).delete)()

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
        'Отправьте чат',
        reply_markup=reply_get_chat_keyboard,
    )
    await state.set_state(ChatState.chat_id)


@router.message(
    StateFilter(ChatState.chat_id),
    F.chat_shared,
)
async def chat_shared_handler(
        message: types.Message,
        state: FSMContext,
):
    chat_id = message.chat_shared.chat_id
    chat_exists: bool = await sync_to_async(
        Chat.objects.filter(chat_id=chat_id).exists
    )()

    if chat_exists:
        await message.answer('Этот чат уже добавлен.')
        return

    await state.update_data(chat_id=chat_id)
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

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    await Chat.objects.acreate(
        **state_data,
        telegram_user_id=telegram_user.id
    )

    await message.answer(
        '<b>Чат успешно добавлен ✅</b>',
        reply_markup=reply_menu_keyboard
    )



