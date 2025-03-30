from typing import Union

from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AbstractTelegramUser,
    LanguageMixin,
)
from web.apps.bots.models import (
    RussianBotTexts,
    EnglishBotTexts,
    HebrewBotTexts,
)

BotTextsUnion = Union[
    RussianBotTexts,
    EnglishBotTexts,
    HebrewBotTexts,
]

class TelegramUser(AbstractTelegramUser, LanguageMixin):
    """Модель telegram пользователя"""

    telegram_id = models.BigIntegerField(
        verbose_name=_('Телеграм ID'),
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )
    full_name = models.CharField(
        _('Имя'),
        max_length=200,
        null=True,
        blank=True,
    )
    search = models.BooleanField(
        _('Поиск'),
        default=True,
    )

    time_joined = models.DateTimeField(
        _('Время добавления'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('Telegram пользователи')
        ordering = ['-time_joined']

    def __str__(self):
        return self.full_name if self.full_name else str(self.telegram_id)

    async def get_texts_model(self):
        model = None

        if self.language == LanguageMixin.RUSSIAN:
            model = RussianBotTexts
        elif self.language == LanguageMixin.ENGLISH:
            model =  EnglishBotTexts
        elif self.language == LanguageMixin.HEBREW:
            model = HebrewBotTexts

        if model:
            return await model.aload()

        return None



