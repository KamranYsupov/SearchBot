from typing import Union

from aiogram import types
from aiogram.exceptions import TelegramBadRequest


async def edit_text_or_answer(
    aiogram_type: Union[types.Message, types.CallbackQuery],
    **kwargs,
):
    if isinstance(aiogram_type, types.Message):
        await aiogram_type.answer(**kwargs)

    elif isinstance(aiogram_type, types.CallbackQuery):
        await aiogram_type.message.edit_text(**kwargs)

    