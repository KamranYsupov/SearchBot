from copy import copy

from django.contrib import admin

from .models import (
    UserBot,
    BotKeyboard,
    BotKeyboardButton,
    RussianBotTexts,
    EnglishBotTexts,
    HebrewBotTexts,
)
from web.admin.mixins import (
    SingletonModelAdmin,
    CreateNotPermittedModelAdminMixin,
    DeleteNotPermittedModelAdminMixin,
)


@admin.register(UserBot)
class UserBotAdmin(admin.ModelAdmin):
    fields = (
        'telegram_id',
        'name',
        'api_id',
        'api_hash',
        'phone_number',
        'session_string',
    )
    readonly_fields = (
        'api_id',
        'api_hash',
    )

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return ()

        return self.readonly_fields


class BotKeyboardButtonInline(
    admin.StackedInline,
):
    model = BotKeyboardButton
    extra = 1

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0

        return self.extra

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

@admin.register(BotKeyboard)
class BotKeyboardAdmin(
    CreateNotPermittedModelAdminMixin,
    DeleteNotPermittedModelAdminMixin,
    admin.ModelAdmin,

):
    exclude = ('slug',)

    inlines = [BotKeyboardButtonInline]


class BotTextsMixinAdmin(SingletonModelAdmin):
    fieldsets = (
        ('Основные тексты', {
            'fields': (
                'permission_denied_text',
                'choice_language_message_text',
                'choice_action_text',
                'cancel_text',
                'sure_text',
                'wait_text',
            )
        }),
        ('Тексты кнопок', {
            'fields': (
                'add_button_text',
                'delete_button_text',
                'back_button_text',
                'yes_button_text',
                'no_button_text',
                'turn_on_search_button_text',
                'turn_off_search_button_text',
            )
        }),
        ('Тексты списков', {
            'fields': (
                'projects_list_button_text',
                'chats_list_button_text',
                'keywords_list_button_text',
                'projects_list_text',
                'chats_list_text',
                'keywords_list_text',
            )
        }),
        ('Тексты страниц', {
            'fields': (
                'chat_text',
                'keyword_text',
                'lead_chat_button_text',
                'project_chats_button_text',
                'project_keywords_button_text',
            )
        }),
        ('Тексты поиска', {
            'fields': (
                'search_text',
            )
        }),
        ('Тексты проектов', {
            'fields': (
                'ask_send_project_name_text',
                'project_name_max_length_error_text',
                'project_exists_error_text',
                'successful_add_project_text',
                'successful_rm_project_text',
            )
        }),
        ('Тексты чатов', {
            'fields': (
                'ask_send_chat_link_text',
                'chat_exists_error_text',
                'join_chat_error_text',
                'successful_add_chat_text',
                'successful_rm_chat_text',
            )
        }),
        ('Тексты ключевых слов', {
            'fields': (
                'ask_send_keyword_text',
                'keyword_max_length_error_text',
                'keyword_exists_error_text',
                'successful_add_keyword_text',
                'successful_rm_keyword_text',
            )
        }),
        ('Тексты чата для получения лидов', {
            'fields': (
                'lead_chat_exists_error_text',
                'successful_add_lead_chat_text',
                'successful_rm_lead_chat_text',
            )
        }),
        ('Тексты рассылок', {
            'fields': (
                'match_report_text',
                'analytic_match_report_text',
                'share_request_text',
            )
        }),
    )


@admin.register(RussianBotTexts, EnglishBotTexts, HebrewBotTexts)
class BotTextsAdmin(BotTextsMixinAdmin):
    pass
