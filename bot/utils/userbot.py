from typing import Optional, Union, Tuple, List

from asgiref.sync import sync_to_async
from django.conf import settings
from pyrogram import types, Client
from pyrogram.errors import UsernameInvalid, RPCError, UserAlreadyParticipant

from bot.keyboards.reply import get_reply_menu_keyboard
from web.apps.bots.models import UserBot
from web.apps.search.models import Chat


async def join_chat(
        chat_link: str,
        client: Client,
        user_bot: UserBot,
        return_is_private: bool = False
) -> Union[Tuple[Optional[types.Chat], bool], Optional[types.Chat]]:
    chat = None
    is_private = True
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
        client: Client,
        user_bot: UserBot,
) -> bool:
    try:
        await client.leave_chat(chat_id)
        if user_bot.chats_count > 0:
            user_bot.chats_count -= 1
            await user_bot.asave()
    except RPCError:
        return False

    return True


def get_client(
        name: str,
        clients: List[Client],
) -> Client | None:

    for client in clients:
        if client.name != name:
            continue

        return client

