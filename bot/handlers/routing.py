from aiogram import Router

from .start import router as start_router
from .search import router as search_router
from .project import router as project_router
from .chat import router as chat_router
from .keyword import router as keyword_router

def get_main_router():
    main_router = Router()

    main_router.include_router(start_router)
    main_router.include_router(search_router)
    main_router.include_router(project_router)
    main_router.include_router(chat_router)
    main_router.include_router(keyword_router)

    return main_router