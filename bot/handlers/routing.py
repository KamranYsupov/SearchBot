from aiogram import Router

from .start import router as start_router
from .search import router as search_router

def get_main_router():
    main_router = Router()

    main_router.include_router(start_router)
    main_router.include_router(search_router)

    return main_router