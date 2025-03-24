from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AsyncBaseModel,
)


class Chat(AsyncBaseModel):
    """Модель telegram чата"""

    link = models.URLField(_('Ссылка'))

    telegram_user = models.ForeignKey(
        'telegram_users.TelegramUser',
        related_name='chats',
        verbose_name=_('Пользователь'),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.link


class Keyword(AsyncBaseModel):
    """Модель ключевого слова"""

    text = models.CharField(
        _('Текст'),
        max_length=150,
        db_index=True,
    )

    chat = models.ForeignKey(
        'search.Chat',
        related_name='keywords',
        verbose_name=_('Чат'),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text