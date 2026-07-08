import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import DEFAULT_JWT_SECRET, settings
from app.core.database import Base, engine

# Import feature models so they register on Base.metadata before create_all.
from app.features.auth import models as auth_models  # noqa: F401
from app.features.tutor import models as tutor_models  # noqa: F401

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.jwt_secret == DEFAULT_JWT_SECRET:
        logger.warning(
            "JWT_SECRET is the insecure default — set a strong random JWT_SECRET "
            "in .env before deploying (tokens are otherwise forgeable)."
        )
    # Create tables on startup (use Alembic for real migrations in production).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Adaptive AI Tutor", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
