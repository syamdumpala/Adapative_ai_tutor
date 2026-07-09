"""Route index — aggregates every feature router into a single API router."""

from fastapi import APIRouter

from app.features.auth.routes import router as auth_router
from app.features.catalog.routes import router as catalog_router
from app.features.teacher.routes import router as teacher_router
from app.features.tutor.routes import me_router
from app.features.tutor.routes import router as tutor_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(catalog_router)
api_router.include_router(tutor_router)
api_router.include_router(me_router)
api_router.include_router(teacher_router)
