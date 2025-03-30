from typing import Union, List

import loguru
from aiogram import Router, types, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.handlers.state import ProjectState
from bot.handlers.utils import array_settings_handler, list_handler
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import get_reply_menu_keyboard, reply_cancel_keyboard
from bot.utils.userbot import leave_chat
from web.apps.bots.models import UserBot, BotKeyboard
from web.apps.search.models import Chat, Project
from web.apps.telegram_users.models import TelegramUser, BotTextsUnion

router = Router()

@router.message(
    or_f(F.text.startswith('❌ '), F.text.endswith(' ❌'))
)
async def cancel_handler(
        message: types.Message,
        state: FSMContext,
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    if not telegram_user:
        return

    texts_model: BotTextsUnion = await telegram_user.get_texts_model()
    menu_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='menu')

    await message.answer(
        texts_model.cancel_text,
        reply_markup=await menu_keyboard.as_markup(
            language=telegram_user.language
        ),
    )
    await state.clear()


@router.message(F.text.startswith('📁 '), F.text.endswith(' 📁'))
@router.callback_query(F.data == 'projects_settings')
async def projects_settings_handler(
        aiogram_type: Union[types.Message, types.CallbackQuery],
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=aiogram_type.from_user.id
    )
    projects = await Project.objects.afilter(telegram_user_id=telegram_user.id)

    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await array_settings_handler(
        aiogram_type,
        list_button_text=texts_model.projects_list_button_text,
        callback_prefix='project',
        array=projects,
        message_text=texts_model.choice_action_text,
        add_button_text=texts_model.add_button_text,
        back_button_text=texts_model.back_button_text,
    )


@router.callback_query(F.data.startswith('projects_list_'))
async def projects_list_callback_handler(
    callback: types.CallbackQuery,
):
    page_number = int(callback.data.split('_')[-1])
    projects: List[Project] = await Project.objects.a_all()

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    await list_handler(
        callback,
        callback_prefix='project',
        array=projects,
        button_text_obj_attr_name='name',
        page_number=page_number,
        per_page=settings.PROJECTS_PER_PAGE,
        message_text=texts_model.projects_list_text,
        back_button_text=texts_model.back_button_text,
    )


@router.callback_query(F.data.startswith('project_'))
async def project_callback_handler(
        callback: types.CallbackQuery,
):
    project_id, previous_page_number = callback.data.split('_')[-2:]
    project: Project = await Project.objects.aget(id=project_id)
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons_callback_data = f'{project.id}_{previous_page_number}'

    buttons = {
        texts_model.lead_chat_button_text : f'lead_chat_{buttons_callback_data}',
        texts_model.project_chats_button_text: f'p_chats_{buttons_callback_data}',
        texts_model.project_keywords_button_text : f'p_kws_{buttons_callback_data}',
        texts_model.delete_button_text : f'ask_rm_project_{buttons_callback_data}',
        texts_model.back_button_text : f'projects_list_{previous_page_number}'
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
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    buttons = {
        texts_model.yes_button_text: f'rm_project_{project_id}',
        texts_model.no_button_text: f'project_{project_id}_{previous_page_number}'
    }
    await callback.message.edit_text(
        texts_model.sure_text,
        reply_markup=get_inline_keyboard(buttons=buttons),
    )


@router.callback_query(F.data.startswith('rm_project_'))
async def rm_project_callback_handler(
        callback: types.CallbackQuery,
):
    project_id = callback.data.split('_')[-1]
    project: Project = await Project.objects.aget(id=project_id)
    project_chats: List[Chat] = await Chat.objects.afilter(project_id=project.id)

    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    if project_chats:
        await callback.message.edit_text(texts_model.wait_text)

        user_bot: UserBot = await UserBot.objects.aget(id=project_chats[0].user_bot_id)

        for chat in project_chats:
            if chat.user_bot_id != user_bot.id:
                user_bot: UserBot = await UserBot.objects.aget(
                    id=chat.user_bot_id
                )

            await leave_chat(chat.chat_id, user_bot)

    await project.adelete()

    await callback.message.edit_text(
        texts_model.successful_rm_project_text,
        reply_markup=get_inline_keyboard(
            buttons={
                texts_model.back_button_text: f'projects_settings'
            }
        ),
    )


@router.callback_query(F.data == 'add_project')
async def add_project_callback_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=callback.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()
    cancel_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='cancel')
    await callback.message.delete()

    await callback.message.answer(
        texts_model.ask_send_project_name_text,
        reply_markup=await cancel_keyboard.as_markup(
            language=telegram_user.language
        ),
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
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    texts_model: BotTextsUnion = await telegram_user.get_texts_model()

    max_length = 200
    if len(message.text) > max_length:
        await message.answer(
            texts_model.project_name_max_length_error_text.format(
                max_length=max_length
            )
        )
        return

    project_exists: bool = await sync_to_async(
        Project.objects.filter(name=message.text).exists
    )()
    if project_exists:
        await message.answer(texts_model.project_exists_error_text)
        return

    state_data = await state.update_data(name=message.text)
    telegram_user: TelegramUser = await TelegramUser.objects.aget(
        telegram_id=message.from_user.id
    )
    await Project.objects.acreate(
        **state_data,
        telegram_user_id=telegram_user.id
    )

    menu_keyboard: BotKeyboard = await BotKeyboard.objects.aget(slug='menu')
    await message.answer(
        texts_model.successful_add_project_text,
        reply_markup=await menu_keyboard.as_markup(language=telegram_user.language)
    )
    await state.clear()
