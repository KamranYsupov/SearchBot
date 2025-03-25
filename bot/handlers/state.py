from aiogram.fsm.state import StatesGroup, State


class ChatState(StatesGroup):
    chat_id = State()
    name = State()


class KeywordState(StatesGroup):
    chat_id = State()
    previous_page_number = State()
    text = State()
