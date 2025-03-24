from aiogram import Router

from .start import router as start_router
from .search import router as search_router
from .chat import router as chat_router

def get_main_router():
    main_router = Router()

    main_router.include_router(start_router)
    main_router.include_router(search_router)
    main_router.include_router(chat_router)

    return main_router