import asyncio
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from pyrogram import Client

from web.apps.search.models import (
    Match,
    Chat,
    Keyword,
)
from web.services.telegram import telegram_service
from web.apps.telegram_users.tasks import send_message_task


@shared_task(ignore_result=True)
def send_keyword_search_matches():
    matches = (
        Match.objects
        .select_related('keyword__chat__telegram_user')
        .filter(is_reported=False)
    )
    message_template = (
        'Найдено совпадение слова <em>{keyword}</em> '
        'в чате <b>{chat}</b>!\n\n'
        
        '<a href="{message_link}">'
        '<b><em>Ссылка на сообщение</em></b>'
        '</a>'
    )


    for match in matches:
        message = message_template.format(
            keyword=match.keyword.text,
            chat=match.keyword.chat.name,
            message_link=match.message_link
        )

        send_message_task.delay(
            chat_id=match.keyword.chat.telegram_user.telegram_id,
            text=message
        )
        match.is_reported = True


    Match.objects.bulk_update(matches, ['is_reported'])

