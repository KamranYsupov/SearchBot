from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AsyncBaseModel,
)
from pyrogram import Client


class UserBot(AsyncBaseModel):
    """Модель юзер бота"""
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

    session = models.FileField(
        _('Файл сессии(.session)'),
        upload_to=settings.USERBOTS_SESSIONS_DIR,
        unique=True,
    )

    def __str__(self):
        return f'Юзербот: {self.name}'

    def configure_client(self) -> Client:
        return Client(
            name=self.name,
            api_hash=self.api_hash,
            api_id=self.api_id,
            phone_number=self.phone_number,
            workdir=self.session.upload_to,
        )