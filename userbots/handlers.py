from asgiref.sync import sync_to_async
from django.db.models.functions import Lower
from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler

from userbots.utils.search import keyword_search
from web.apps.search.models import Keyword, Match, Chat
from web.apps.telegram_users.models import TelegramUser


async def find_keyword_in_message_handler_func(client: Client, message: types.Message):
    keywords = await sync_to_async(list)(
        await sync_to_async(Keyword.objects.values_list)('text', flat=True)
    )
    found_keywords_results = keyword_search(message.text, keywords)

    found_keywords = await sync_to_async(
        Keyword.objects
        .annotate(lower_text=Lower('text'))
        .filter
    )(lower_text__in=found_keywords_results)

    matches = []
    # matches = [
    #     Match(message_link=message.link, keyword_id=keyword.id,)
    #     async for keyword in found_keywords
    # ]

    async for keyword in found_keywords:
        matches.append(Match(message_link=message.link, keyword_id=keyword.id))
        chat = await Chat.objects.aget(id=keyword.chat_id)
        telegram_user = await TelegramUser.objects.aget(id=chat.telegram_user_id)

        await client.send_message(
            chat_id=telegram_user.telegram_id,
            text=f'Найдено совпадение: {message.link}',
        )

    await sync_to_async(Match.objects.bulk_create)(matches)


message_handler = MessageHandler(
    find_keyword_in_message_handler_func,
    filters=((filters.channel | filters.group) & filters.text)
)