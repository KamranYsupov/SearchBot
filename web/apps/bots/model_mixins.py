from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import SingletonModel


class TelegramMessageTextField(models.CharField):
    description = _('Telegram message text')

    def __init__(self, *args, db_collation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_length = 4096


class BotTextsMixin(SingletonModel):
    """Миксин текстов бота"""
    permission_denied_text = TelegramMessageTextField(
        _('Текст "Отказано в доступе ❌"')
    )
    choice_language_message_text = TelegramMessageTextField(
        _('Текст изменения языка')
    )
    choice_action_text = TelegramMessageTextField(
        _('Текст "Выберите действие"')
    )
    cancel_text = TelegramMessageTextField(
        _('Текст после нажатии кнопки "Отмена ❌"')
    )
    sure_text = TelegramMessageTextField(
        _('Текст перед удалением ("Вы уверены?")')
    )
    wait_text = TelegramMessageTextField(
        _('Текст ожидания ("Подожите . . .")')
    )
    add_button_text = TelegramMessageTextField(
        _('Текст кнопки "Добавить ➕"')
    )
    delete_button_text = TelegramMessageTextField(
        _('Текст кнопки "Удалить 🗑"')
    )
    back_button_text = TelegramMessageTextField(
        _('Текст кнопки "Назад 🔙"')
    )
    yes_button_text = TelegramMessageTextField(
        _('Текст кнопки "Да"')
    )
    no_button_text = TelegramMessageTextField(
        _('Текст кнопки "Нет"')
    )

    search_text = TelegramMessageTextField(
        _('Текст сообщения поиска')
    )
    turn_on_search_button_text = TelegramMessageTextField(
        _('Текст кнопки включения поиска 🔎')
    )
    turn_off_search_button_text = TelegramMessageTextField(
        _('Текст кнопки выключения поиска 🔎')
    )


    projects_list_button_text = TelegramMessageTextField(
        _('Текст кнопки "Список проектов 🗂"')
    )
    chats_list_button_text = TelegramMessageTextField(
        _('Текст кнопки "Список чатов 🗂"')
    )
    keywords_list_button_text = TelegramMessageTextField(
        _('Текст кнопки "Список ключевых слов 🗂"')
    )

    projects_list_text = TelegramMessageTextField(
        _('Текст на странице списка проектов')
    )
    chats_list_text = TelegramMessageTextField(
        _('Текст на странице списка чатов')
    )
    keywords_list_text = TelegramMessageTextField(
        _('Текст на странице списка ключевых слов')
    )

    chat_text = TelegramMessageTextField(
        _('Текст на странице чата')
    )
    keyword_text = TelegramMessageTextField(
        _('Текст на странице ключевого слова')
    )

    lead_chat_button_text = TelegramMessageTextField(
        _('Текст кнопки "📥 Группа для получения лидов 📥"')
    )
    project_chats_button_text = TelegramMessageTextField(
        _('Текст кнопки "⚙️ Настройка групп для отслеживания ⚙️"')
    )
    project_keywords_button_text = TelegramMessageTextField(
        _('Текст кнопки "💬 Ключевые слова  💬"')
    )


    # Проект
    ask_send_project_name_text = TelegramMessageTextField(
        _('Текст просьбы отправить название проекта при добавлении')
    )
    project_name_max_length_error_text = TelegramMessageTextField(
        _('Текст ошибки превышения максимальной длинны названия проекта')
    )
    project_exists_error_text = TelegramMessageTextField(
        _('Текст ошибки "Проект уже добавлен"')
    )
    successful_add_project_text = TelegramMessageTextField(
        _('Текст успешного добавления проекта')
    )
    successful_rm_project_text = TelegramMessageTextField(
        _('Текст успешного удаления проекта')
    )

    # Чат
    ask_send_chat_link_text = TelegramMessageTextField(
        _('Текст просьбы отправить ссылку чата при добавлении')
    )
    chat_exists_error_text = TelegramMessageTextField(
        _('Текст ошибки "Чат уже добавлен"')
    )
    join_chat_error_text = TelegramMessageTextField(
        _('Текст ошибки присоединения к чату')
    )
    successful_add_chat_text = TelegramMessageTextField(
        _('Текст успешного добавления чата')
    )
    successful_rm_chat_text = TelegramMessageTextField(
        _('Текст успешного удаления чата')
    )

    # Ключевое слово
    ask_send_keyword_text = TelegramMessageTextField(
        _('Текст просьбы отправить ключевое слово при добавлении')
    )
    keyword_max_length_error_text = TelegramMessageTextField(
        _('Текст ошибки превышения максимальной длинны ключевого слова')
    )
    keyword_exists_error_text = TelegramMessageTextField(
        _('Текст ошибки "Ключевое слово уже добавлено в проект"')
    )
    successful_add_keyword_text = TelegramMessageTextField(
        _('Текст успешного добавления ключевого слова')
    )
    successful_rm_keyword_text = TelegramMessageTextField(
        _('Текст успешного удаления ключевого слова')
    )

    # Чат для получения лидов
    lead_chat_exists_error_text = TelegramMessageTextField(
        _('Текст ошибки "Этот чат уже добавлен другим пользователем"')
    )
    successful_add_lead_chat_text = TelegramMessageTextField(
        _('Текст успешного добавления чата для получения лидов')
    )
    successful_rm_lead_chat_text = TelegramMessageTextField(
        _('Текст успешного удаления чата для получения лидов')
    )

    class Meta:
        verbose_name = 'Тексты бота'
        abstract = True

    def __str__(self):
        return self.Meta.verbose_name