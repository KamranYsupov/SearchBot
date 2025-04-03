from collections.abc import Sequence

from dependency_injector import containers, providers
from django.conf import settings

from pyrogram import Client
from telethon import TelegramClient
from telethon.sessions import StringSession

from web.apps.bots.models import UserBot


class Container(containers.DeclarativeContainer):
    user_bots: Sequence[UserBot] = UserBot.objects.all()

    pyrogram_client_1 = providers.Singleton(
        Client,
        name=user_bots[0].name,
        api_id=user_bots[0].api_id,
        api_hash=user_bots[0].api_hash,
        phone_number=user_bots[0].phone_number,
        session_string=user_bots[0].pyrogram_session_string
    )
    telethon_client_1 = providers.Singleton(
        TelegramClient,
        session=StringSession(user_bots[0].telethon_session_string),
        api_id=user_bots[0].api_id,
        api_hash=user_bots[0].api_hash,
    )


