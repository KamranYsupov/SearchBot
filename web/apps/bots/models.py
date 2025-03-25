import asyncio
import os
import sqlite3

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AsyncBaseModel,
)
from pyrogram import Client


class UserBot(AsyncBaseModel):
    """Модель юзер бота"""
    telegram_id = models.BigIntegerField(
        verbose_name=_('Телеграм ID'),
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        _('Имя пользователя'),
        max_length=100,
        unique=True,
        db_index=True
    )
    api_id = models.CharField(
        max_length=70,
        unique=True,
    )
    api_hash = models.CharField(
        max_length=70,
        unique=True,
    )
    phone_number = models.CharField(
        _('Номер телефона'),
        max_length=25,
        unique=True,
        db_index=True
    )

    session_1 = models.FileField(
        _('Файл сессии 1(.session)'),
        upload_to=settings.USER_BOTS_SESSIONS_DIR_1,
        unique=True,
    )
    session_2 = models.FileField(
        _('Файл сессии 2(.session)'),
        upload_to=settings.USER_BOTS_SESSIONS_DIR_2,
        unique=True,
    )

    chats_count = models.PositiveIntegerField(
        _('Количество чатов'),
        default=0,
    )

    def __str__(self):
        return f'Юзербот: {self.name}'

    def configure_client(
            self,
            session_workdir: str = str(settings.USER_BOTS_SESSIONS_ROOT_1)
    ) -> Client:
        client = Client(
            name=self.name,
            api_hash=self.api_hash,
            api_id=self.api_id,
            phone_number=self.phone_number,
            workdir=session_workdir,
        )

        return client
