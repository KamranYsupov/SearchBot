from asgiref.sync import sync_to_async
from django.db import models
from django.utils.translation import gettext_lazy as _
from ulid import ULID

from .base_manager import AsyncBaseManager
        
        
def ulid_default() -> str:
    return str(ULID())
        
        
class AsyncBaseModel(models.Model):
    id = models.CharField( 
        primary_key=True,
        default=ulid_default,
        max_length=26,
        editable=False,
        unique=True,
        db_index=True,
    )
    
    objects = AsyncBaseManager()
    
    class Meta: 
        abstract = True
        
        
class AbstractTelegramUser(AsyncBaseModel):
    telegram_id = models.BigIntegerField(
        verbose_name=_('Телеграм ID'),
        unique=True,
        db_index=True,
    )
    username = models.CharField(
        _('Имя пользователя'),
        max_length=70,
        unique=True,
        db_index=True,
        null=True,
    )
    
    class Meta: 
        abstract = True
    
    
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата последнего обновления'),
        auto_now=True
    )

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """Singelton модель"""

    def save(self, *args, **kwargs):
        if self.__class__.objects.count() == 0:
            super().save(*args, **kwargs)
        else:
            existing = self.__class__.objects.get()
            self.id = existing.id
            super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    @sync_to_async
    def aload(cls):
        return cls.load()

    class Meta:
        abstract = True


class LanguageMixin(models.Model):
    RUSSIAN = 'Russian'
    ENGLISH = 'English'
    HEBREW = 'Hebrew'

    CHOICES = (
        (RUSSIAN, 'Русский'),
        (ENGLISH, 'Английский'),
        (HEBREW, 'Иврит')
    )

    language = models.CharField(
        _('Язык'),
        choices=CHOICES,
        default=RUSSIAN,
        max_length=10,
        db_index=True
    )

    class Meta:
        abstract = True
