from aiogram import Router

from .start import router as start_router
from .search import router as search_router
from .project import router as project_router
from .chat import router as chat_router
from .keyword import router as keyword_router
from bot.middlewares.throttling import rate_limit_middleware


def get_main_router():
    main_router = Router()

    main_router.include_routers(
        start_router,
        search_router,
        project_router,
        chat_router,
        keyword_router,
    )
    main_router.message.middleware(rate_limit_middleware)

    return main_router