import asyncio
from datetime import timedelta

import loguru
from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from pyrogram import Client

from web.apps.search.models import (
    Match,
    Chat,
    Keyword, Project,
)
from web.apps.telegram_users.models import TelegramUser, BotTextsUnion
from web.db.model_mixins import LanguageMixin
from web.services.telegram import telegram_service
from web.apps.telegram_users.tasks import send_message_task


@shared_task(ignore_result=True)
def send_keyword_search_matches():
    telegram_users: list[TelegramUser] = (
        TelegramUser.objects
        .prefetch_related('projects__chats', 'projects__keywords')
        .filter(search=True)
    )

    now = timezone.now()
    yesterday = now - timedelta(days=1)
    yesterday_date_str = yesterday.date().strftime('%d.%m.%Y')

    update_matches = []

    for telegram_user in telegram_users:
        texts_model: BotTextsUnion = async_to_sync(
            telegram_user.get_texts_model
        )()

        report_text = texts_model.analytic_match_report_text.format(
            date=yesterday_date_str
        ) + '\n\n'

        for project in telegram_user.projects.all():
            for keyword in project.keywords.all():
                matches = list(Match.objects.filter(
                    is_reported=False,
                    keyword__id=keyword.id
                ))

                report_text += f'{keyword.text}: <em>{len(matches)}</em>\n\n'
                update_matches.extend(matches)

        for i in range(0, len(report_text), 4000):
            chunk_text = report_text[i:i + 4000]

            send_message_task.delay(
                chat_id=telegram_user.telegram_id,
                text=chunk_text
            )

    for match in update_matches:
        match.is_reported = True

    Match.objects.bulk_update(update_matches, ['is_reported'])


@shared_task(ignore_result=True)
def forward_match_message_and_send_match_info(match_id: str):
    match = Match.objects.get(id=match_id)
    lead_chat_id = match.keyword.project.lead_chat_id
    telegram_user = match.keyword.project.telegram_user
    texts_model: BotTextsUnion = async_to_sync(
        telegram_user.get_texts_model
    )()

    forward_message_response = telegram_service.forward_message(
        chat_id=lead_chat_id,
        from_chat_id=settings.KEYWORDS_MATCHES_BUFFER_GROUP_ID,
        message_id=int(match.message_id),
    )
    forward_message_data = forward_message_response.json()

    message_text = texts_model.match_report_text.format(
        keyword=match.keyword.text,
        chat=match.chat.name,
        author=f'@{match.from_user_username}' if match.from_user_username else '-',
        message_link=match.message_link if not match.chat.is_private else '-',
    )
    reply_to_message_id = forward_message_data['result']['message_id']

    telegram_service.send_message(
        chat_id=lead_chat_id,
        text=message_text,
        reply_to_message_id=reply_to_message_id,
    )

