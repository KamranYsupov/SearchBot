from aiogram.fsm.state import StatesGroup, State


class ChatState(StatesGroup):
    chat_id = State()
    name = State()
