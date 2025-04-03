import loguru
from asgiref.sync import sync_to_async
from dependency_injector.wiring import Provide, inject
from django.conf import settings
from django.db.models.functions import Lower
from pyrogram import Client, types, filters
from pyrogram.errors import BadRequest
from pyrogram.handlers import MessageHandler
from telethon import events

from bot.container import Container
from bot.utils.userbot import get_client
from userbots.utils.search import keyword_search
from userbots.utils.message import get_message_link
from web.apps.search.models import Chat, Keyword, Match


@inject
async def handle_groups(
        event: events.NewMessage.Event,
        pyrogram_client_1: Client = Provide[Container.pyrogram_client_1],
):
    if not event.is_group and not event.is_channel:
        return

    if event.chat_id == settings.KEYWORDS_MATCHES_BUFFER_GROUP_ID:
        return

    chats = await sync_to_async(list)(
        await sync_to_async(
            Chat.objects
            .select_related('user_bot')
            .filter
        )(chat_id=event.chat_id)
    )
    if not chats:
        return

    event_chat = await event.get_chat()
    event_sender = await event.get_sender()

    keywords = await sync_to_async(list)(
        await sync_to_async(Keyword.objects.values_list)('text', flat=True)
    )
    found_keywords_results = keyword_search(event.message.message, keywords)
    clients = [pyrogram_client_1]

    for chat in chats:
        if not chat or not chat.project_id:
            continue

        found_keywords = await sync_to_async(
            Keyword.objects
            .select_related('project__telegram_user')
            .annotate(lower_text=Lower('text'))
            .filter
        )(
            lower_text__in=found_keywords_results,
            project_id=chat.project_id,
        )
        pyrogram_client = get_client(name=chat.user_bot.name, clients=clients)
        if not pyrogram_client:
            continue

        try:
            await pyrogram_client.start()
        except ConnectionError:
            pass

        async for keyword in found_keywords:
            if not keyword.project.telegram_user.search:
                continue

            match = Match(
                message_link=get_message_link(event_chat, event.message.id),
                from_user_username=event_sender.username,
                chat_id=chat.id,
                keyword_id=keyword.id
            )

            forwarded_message_id = None

            try:
                forwarded_messages = await pyrogram_client.forward_messages(
                    chat_id=settings.KEYWORDS_MATCHES_BUFFER_GROUP_ID,
                    from_chat_id=event.chat_id,
                    message_ids=[event.message.id],
                )
                forwarded_message_id = forwarded_messages[0].id
            except BadRequest:
                pass

            match.message_id = forwarded_message_id
            await match.asave()
