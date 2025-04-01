from typing import Optional, Union, Tuple

from asgiref.sync import sync_to_async
from django.conf import settings
from pyrogram import types, Client
from pyrogram.errors import UsernameInvalid, RPCError, UserAlreadyParticipant

from bot.keyboards.reply import get_reply_menu_keyboard
from web.apps.bots.models import UserBot
from web.apps.search.models import Chat


async def join_chat(
        chat_link: str,
        user_bot: UserBot,
        user_bot_session_workdir: str = settings.USER_BOTS_SESSIONS_ROOT_2,
        return_is_private: bool = False
) -> Union[Tuple[Optional[types.Chat], bool], Optional[types.Chat]]:
    chat = None
    is_private = True

    async with user_bot.configure_client(
            session_workdir=user_bot_session_workdir
    ) as client:

        try:
            chat_id = chat_link
            try:
                chat = await client.join_chat(chat_id)
            except UsernameInvalid:
                chat_id = chat_link.split('/')[-1]
                is_private = False
                chat = await client.join_chat(chat_id)
        except UserAlreadyParticipant:
            chat = await client.get_chat(chat_id)
        except RPCError:
            pass

        if chat is None:
            return None if not return_is_private else None, is_private

        user_bot.chats_count += 1
        await user_bot.asave()

    return chat, is_private


async def leave_chat(
        chat_id: Union[int, str],
        user_bot: UserBot,
        user_bot_session_workdir: str = settings.USER_BOTS_SESSIONS_ROOT_2
) -> bool:
    async with user_bot.configure_client(
            session_workdir=user_bot_session_workdir
    ) as client:
        try:
            await client.leave_chat(chat_id)
            user_bot.chats_count -= 1
            await user_bot.asave()
        except RPCError:
            return False

    return True


