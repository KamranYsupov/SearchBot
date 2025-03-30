from aiogram import Router

from .start import router as start_router
from .search import router as search_router
from .project import router as project_router
from .chat import router as chat_router
from .keyword import router as keyword_router
from .lang import router as lang_router
from .lead_chat import router as lead_chat_router

def get_main_router():
    main_router = Router()

    main_router.include_routers(
        start_router,
        search_router,
        project_router,
        chat_router,
        keyword_router,
        lang_router,
        lead_chat_router
    )

    return main_router