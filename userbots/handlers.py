import loguru
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models.functions import Lower
from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler

from bot.loader import bot
from userbots.utils.search import keyword_search
from web.apps.search.models import Chat, Keyword, Match


async def find_keyword_in_message_handler_func(client: Client, message: types.Message):
    chats = await Chat.objects.afilter(chat_id=message.chat.id)
    if not chats:
        return

    keywords = await sync_to_async(list)(
        await sync_to_async(Keyword.objects.values_list)('text', flat=True)
    )
    found_keywords_results = keyword_search(message.text, keywords)

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
        async for keyword in found_keywords:
            if not keyword.project.telegram_user.search:
                continue

            forwarded_messages = await client.forward_messages(
                chat_id=settings.KEYWORDS_MATCHES_BUFFER_GROUP_ID,
                from_chat_id=message.chat.id,
                message_ids=[message.id]
            )

            match = Match(
                message_id=forwarded_messages[0].id,
                message_link=message.link,
                from_user_username=message.from_user.username,
                chat_id=chat.id,
                keyword_id=keyword.id
            )
            await match.asave()


message_handler = MessageHandler(
    find_keyword_in_message_handler_func,
    filters=((filters.channel | filters.group) & filters.text)
)