def get_message_link(chat, message_id: int) -> str:
    if chat.username:  # Публичный чат (@username)
        message_link = f'https://t.me/{chat.username}/{message_id}'
    else:  # Приватный чат/канал
        raw_chat_id = str(chat.id)
        if raw_chat_id.startswith('-100'):
            chat_id = raw_chat_id[4:]  # Убираем '-100'
            message_link = f'https://t.me/c/{chat_id}/{message_id}'
        else:
            message_link = f'https://t.me/c/{chat.id}/{message_id}'

    return message_link