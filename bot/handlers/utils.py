from typing import Union, Optional, Sequence

from aiogram import types

from bot.keyboards.inline import get_inline_keyboard
from bot.utils.bot import edit_text_or_answer
from bot.utils.pagination import Paginator, get_pagination_buttons


async def array_settings_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
        callback_prefix: str,
        list_button_text: str,
        array: Optional[Sequence] = None,
        list_button_data: Optional[str] = None,
        add_button_data: Optional[str] = None,
        back_button_data: Optional[str] = None,
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


async def list_handler(
        callback: types.CallbackQuery,
        page_number: int,
        per_page: int,
        array: Sequence,
        button_text_obj_attr_name: str,
        callback_prefix: str,
        message_text: Optional[str] = 'Выберите вариант',
        back_button_callback_data: Optional[str] = None,
        pagination_buttons_prefix: Optional[str] = None,
        lang: Optional[str] = 'ru',
):
    paginator = Paginator(
        array=array,
        page_number=page_number,
        per_page=per_page,
    )

    buttons = {
        getattr(obj, button_text_obj_attr_name): \
            f'{callback_prefix}_{obj.id}_{page_number}'
        for obj in paginator.get_page()
    }
    pagination_buttons = get_pagination_buttons(
        paginator, prefix=f'{callback_prefix}s_list' if not pagination_buttons_prefix \
        else pagination_buttons_prefix
    )
    sizes = (1,) * per_page

    if not pagination_buttons:
        pass
    elif len(pagination_buttons.items()) == 1:
        sizes += (1, 1)
    else:
        sizes += (2, 1)

    buttons.update(pagination_buttons)

    if not back_button_callback_data:
        back_button_callback_data = f'{callback_prefix}s_settings'
    buttons['Назад 🔙'] = back_button_callback_data

    await callback.message.edit_text(
        message_text,
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=sizes,
        ),
    )