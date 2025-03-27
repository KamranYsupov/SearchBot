from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AbstractTelegramUser,
)


class TelegramUser(AbstractTelegramUser):
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

    keywords_chat_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        default=None,
        blank=True,
    )
    keywords_chat_link = models.URLField(
        max_length=70,
        unique=True,
        null=True,
        default=None,
        blank=True
    )

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('Telegram пользователи')
        ordering = ['-time_joined']

    def __str__(self):
        return self.full_name if self.full_name else str(self.telegram_id)