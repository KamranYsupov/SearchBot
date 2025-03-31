from copy import copy

from django.contrib import admin

from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id',
        'full_name',
        'username',
        'time_joined'
    ]

    fields = copy(list_display)
    readonly_fields = copy(fields)


    def get_fields(self, request, obj=None):
        if not obj:
            return ('telegram_id', )

        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return self.readonly_fields[1:] # .remove('telegram_id')

        return self.readonly_fields

