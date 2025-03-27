from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AsyncBaseModel, TimestampMixin,
)


class Project(AsyncBaseModel):
    """Модель проекта"""
    name = models.CharField(
        _('Название'),
        max_length=200,
    )
    telegram_user = models.ForeignKey(
        'telegram_users.TelegramUser',
        related_name='chats',
        verbose_name=_('Пользователь'),
        on_delete=models.CASCADE,
    )


class Chat(AsyncBaseModel):
    """Модель telegram чата"""
    chat_id = models.CharField(max_length=50, db_index=True)
    chat_link = models.URLField(max_length=70, db_index=True)
    name = models.CharField(
        _('Название'),
        max_length=130,
    )

    user_bot = models.ForeignKey(
        'bots.UserBot',
        related_name='chats',
        verbose_name=_('Юзер бот'),
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(
        'search.Project',
        related_name='chats',
        verbose_name=_('проект'),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Keyword(AsyncBaseModel):
    """Модель ключевого слова"""

    text = models.TextField(
        _('Текст'),
        max_length=150,
        db_index=True,
    )

    project = models.ForeignKey(
        'search.Project',
        related_name='keywords',
        verbose_name=_('проект'),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text


class Match(AsyncBaseModel, TimestampMixin):
    """Модель совпадения слова в тексте"""
    message_link = models.URLField(_('Ссылка на сообщение'))
    message_id = models.PositiveIntegerField(_('ID сообщения в буферной группе'))
    is_reported = models.BooleanField(_('Отправлен'), default=False)
    updated_at = None

    keyword = models.ForeignKey(
        'search.Keyword',
        verbose_name=_('Ключевое слово'),
        on_delete=models.CASCADE,
        db_index=True,
    )
