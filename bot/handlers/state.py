from aiogram.fsm.state import StatesGroup, State


class ProjectState(StatesGroup):
    name = State()


class ChatState(StatesGroup):
    project_id = State()
    previous_page_number = State()
    chat_link = State()
    name = State()


class KeywordState(StatesGroup):
    project_id = State()
    previous_page_number = State()
    text = State()


class KeywordsChatState(StatesGroup):
    chat_id = State()
    chat_link = State()

