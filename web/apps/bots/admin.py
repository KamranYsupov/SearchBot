from copy import copy

from django.contrib import admin

from .models import UserBot


@admin.register(UserBot)
class UserBotAdmin(admin.ModelAdmin):
    fields = (
        'telegram_id',
        'name',
        'api_id',
        'api_hash',
        'phone_number',
        'session_1',
        'session_2',
    )
    readonly_fields = (
        'api_id',
        'api_hash',
    )

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return ()

        return self.readonly_fields
