from __future__ import annotations

from fastapi import APIRouter

from api.auth import router as auth_router
from api.chat import router as chat_router
from api.documents import router as documents_router
from api.tickets import router as tickets_router
from api.users import router as users_router
from api.admin_rag import router as admin_rag_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(tickets_router)
api_router.include_router(documents_router)
api_router.include_router(users_router)
api_router.include_router(admin_rag_router)
