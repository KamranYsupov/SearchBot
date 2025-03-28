import asyncio
import pprint

import loguru
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.conf import settings

from .models import Match, Keyword
from web.services.telegram import telegram_service

@receiver(post_save, sender=Match)
def order_post_save(sender, instance: Match, created, **kwargs):
    if not created:
        return

    lead_chat_id = instance.keyword.project.lead_chat_id

    forward_message_response = telegram_service.forward_message(
        chat_id=lead_chat_id,
        from_chat_id=settings.KEYWORDS_MATCHES_BUFFER_GROUP_ID,
        message_id=int(instance.message_id),
    )
    forward_message_data = forward_message_response.json()
    pprint.pprint(forward_message_data)
    message_template = (
        'Найдено совпадение слова <em>{keyword}</em> '
        'в чате <b>{chat}</b>!\n\n'

        '<a href="{message_link}">'
        '<b><em>Ссылка на сообщение</em></b>'
        '</a>'
    )
    message_text = message_template.format(
        keyword=instance.keyword.text,
        chat=instance.chat.name,
        message_link=instance.message_link,
    )

    telegram_service.send_message(
        chat_id=lead_chat_id,
        text=message_text,
        reply_to={'reply_to_msg_id': forward_message_data['result']['message_id']},
    )

