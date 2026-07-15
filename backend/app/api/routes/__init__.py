from fastapi import APIRouter

from app.api.routes.categories import router as categories_router
from app.api.routes.chatbot import router as chatbot_router
from app.api.routes.comments import router as comments_router
from app.api.routes.posts import router as posts_router
from app.api.routes.presence import router as presence_router
from app.api.routes.tour import router as tour_router

api_router = APIRouter()
api_router.include_router(categories_router)
api_router.include_router(posts_router)
api_router.include_router(comments_router)
api_router.include_router(tour_router)
api_router.include_router(chatbot_router)
api_router.include_router(presence_router)
