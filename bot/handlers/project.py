from typing import Union, List

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from django.conf import settings

from bot.handlers.state import ProjectState
from bot.handlers.utils import array_settings_handler, list_handler
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import reply_menu_keyboard, reply_cancel_keyboard
from bot.utils.userbot import leave_chat
from web.apps.bots.models import UserBot
from web.apps.search.models import Chat, Project
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


@router.message(F.text.casefold() == '📁 проекты 📁')
@router.callback_query(F.data == 'projects_settings')
async def projects_settings_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=aiogram_type.from_user.id
    )
    projects = await Project.objects.afilter(telegram_user_id=telegram_user.id)

    await array_settings_handler(
        aiogram_type,
        list_button_text='Список проектов 🗂',
        callback_prefix='project',
        array=projects
    )


@router.callback_query(F.data.startswith('projects_list_'))
async def projects_list_callback_handler(
    callback: types.CallbackQuery,
):
    page_number = int(callback.data.split('_')[-1])
    projects: List[Project] = await Project.objects.a_all()
    await list_handler(
        callback,
        callback_prefix='project',
        array=projects,
        button_text_obj_attr_name='name',
        page_number=page_number,
        per_page=settings.PROJECTS_PER_PAGE,
        message_text='Выберите проект.'
    )


@router.callback_query(F.data.startswith('project_'))
async def project_callback_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    project: Project = await Project.objects.aget(id=project_id)

    buttons_callback_data = f'{project.id}_{previous_page_number}'

    buttons = {
        '📥 Группа для получения лидов 📥': f'lead_chat_{buttons_callback_data}',
        '⚙️ Настройка групп для отслеживания ⚙️': f'p_chats_{buttons_callback_data}',
        '💬 Ключевые слова  💬': f'p_kws_{buttons_callback_data}',
        'Удалить 🗑': f'ask_rm_project_{buttons_callback_data}',
        'Назад 🔙': f'projects_list_{previous_page_number}'
    }

    await callback.message.edit_text(
        f'<b>{project.name}</b>',
        reply_markup=get_inline_keyboard(
            buttons=buttons,
            sizes=(1, ) * 4,
        ),
    )


@router.callback_query(F.data.startswith('ask_rm_project_'))
async def ask_rm_project_callback_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]

    await callback.message.edit_text(
        f'<b>Вы уверены?</b>',
        reply_markup=get_inline_keyboard(
            buttons={
                'Да': f'rm_project_{project_id}',
                'Нет': f'project_{project_id}_{previous_page_number}'
            }
        ),
    )


@router.callback_query(F.data.startswith('rm_project_'))
async def rm_project_callback_handler(
        callback: types.CallbackQuery,
):
    project_id = callback.data.split('_')[-1]
    project: Project = await Project.objects.aget(id=project_id)
    project_chats: List[Chat] = await Chat.objects.afilter(project_id=project.id)

    if project_chats:
        wait_text = '<em>Подожите . . .</em>'
        await callback.message.edit_text(wait_text)

        user_bot: UserBot = await UserBot.objects.aget(id=project_chats[0].user_bot_id)

        for chat in project_chats:
            if chat.user_bot_id != user_bot.id:
                user_bot: UserBot = await UserBot.objects.aget(
                    id=chat.user_bot_id
                )

            await leave_chat(chat.chat_id, user_bot)

    await project.adelete()

    await callback.message.edit_text(
        f'<b>Проект успешно удален ✅</b>',
        reply_markup=get_inline_keyboard(
            buttons={'Назад 🔙': f'projects_settings'}
        ),
    )


@router.callback_query(F.data == 'add_project')
async def add_project_callback_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    await callback.message.delete()

    await callback.message.answer(
        'Отправьте название проекта 📝',
        reply_markup=reply_cancel_keyboard,
    )
    await state.set_state(ProjectState.name)


@router.message(
    StateFilter(ProjectState.name),
    F.text,
)
async def process_project_name_handler(
        message: types.Message,
        state: FSMContext,
):
    project_name_max_length = 200
    if len(message.text) > project_name_max_length:
        await message.answer(
            f'Максимальная длина {project_name_max_length} символов'
        )
        return

    state_data = await state.update_data(name=message.text)
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    await Project.objects.acreate(
        **state_data,
        telegram_user_id=telegram_user.id
    )

    await message.answer(
        '<b>Проект успешно добавлен ✅</b>',
        reply_markup=reply_menu_keyboard
    )
    await state.clear()
