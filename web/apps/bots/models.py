import asyncio
import os
import sqlite3
from typing import Optional

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from aiogram.types import ReplyKeyboardMarkup

from bot.keyboards.reply import get_reply_keyboard
from web.apps.bots.model_mixins import BotTextsMixin
from web.db.model_mixins import (
    AsyncBaseModel, LanguageMixin,
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

    pyrogram_session_string = models.TextField(
        _('Строка сессии(pyrogram)'),
        unique=True,
        null=True,
        default=None
    )
    telethon_session_string = models.TextField(
        _('Строка сессии(telethon)'),
        unique=True,
        null=True,
        default=None
    )

    chats_count = models.PositiveIntegerField(
        _('Количество чатов'),
        default=0,
    )

    def __str__(self):
        return f'Юзербот: {self.name}'


class BotKeyboard(AsyncBaseModel):
    """Модель клавиатуры бота"""
    name = models.CharField(
        _('Название'),
        max_length=150,
        unique=True
    )
    slug = models.CharField(
        _('Slug'),
        max_length=150,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('Клавиатура')
        verbose_name_plural = _('Клавиатуры бота')

    def __str__(self):
        return self.name

    @staticmethod
    def get_text_name(language: str) -> Optional[str]:
        text_field_name = 'text'
        if language == LanguageMixin.RUSSIAN:
            text_field_name = f'ru_{text_field_name}'
        elif language == LanguageMixin.ENGLISH:
            text_field_name = f'en_{text_field_name}'
        elif language == LanguageMixin.HEBREW:
            text_field_name = f'he_{text_field_name}'
        else:
            return None

        return text_field_name

    @sync_to_async
    def as_markup(self, language: str) -> Optional[ReplyKeyboardMarkup]:
        text_field_name = self.get_text_name(language)
        buttons = self.buttons.all().values_list(
            text_field_name, flat=True
        )
        keyboard = get_reply_keyboard(buttons=buttons)

        return keyboard


class BotKeyboardButton(AsyncBaseModel):
    """Модель кнопки клавиатуры бота"""

    class Type:
        REPLY = 'Reply'
        INLINE = 'Inline'

        CHOICES = (
            (REPLY, REPLY),
            (INLINE, INLINE),
        )

    name = models.CharField(
        _('Название'),
        max_length=150,
    )
    ru_text = models.CharField(
        _('Текст на русском 🇷🇺'),
        max_length=150,
    )
    en_text = models.CharField(
        _('Текст на ангилйском 🇺🇸'),
        max_length=150,
    )
    he_text = models.CharField(
        _('Текст на иврите 🇮🇱'),
        max_length=150,
    )

    keyboard = models.ForeignKey(
        'bots.BotKeyboard',
        related_name='buttons',
        verbose_name=_('Кнопки'),
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('Кнопка')
        verbose_name_plural = _('Кнопки бота')
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'ru_text',
                    'en_text',
                    'he_text',
                    'keyboard'
                ],
                name='unique_button_text_per_keyboard'
            )
        ]

    def __str__(self):
        return self.name


class RussianBotTexts(BotTextsMixin):
    """Singleton модель текстов бота на русском"""

    class Meta:
        verbose_name = 'Тексты бота на русском'
        verbose_name_plural = verbose_name


class EnglishBotTexts(BotTextsMixin):
    """Singleton модель текстов бота на английском"""

    class Meta:
        verbose_name = 'Тексты бота на английском'
        verbose_name_plural = verbose_name


class HebrewBotTexts(BotTextsMixin):
    """Singleton модель текстов бота на иврите"""

    class Meta:
        verbose_name = 'Тексты бота на иврите'
        verbose_name_plural = verbose_name



