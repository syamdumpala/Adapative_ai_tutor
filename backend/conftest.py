"""Shared pytest fixtures.

Tests run against an in-memory SQLite database (via aiosqlite) so they require
neither a running PostgreSQL instance nor an Anthropic API key. The `get_db`
dependency is overridden to use the test database.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db

# Import models so their tables register on Base.metadata.
from app.features.auth import models as _auth_models  # noqa: F401
from app.features.catalog import models as _catalog_models  # noqa: F401
from app.features.tutor import models as _tutor_models  # noqa: F401
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


async def _make_client(seed_demo: bool, with_analytics: bool = False):
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if seed_demo:
        from app.seed import seed  # imported lazily so plain tests stay fast

        async with TestSession() as session:
            await seed(session, with_analytics=with_analytics)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    return engine, transport


@pytest_asyncio.fixture
async def client():
    engine, transport = await _make_client(seed_demo=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_client():
    """A client backed by the demo seed dataset (subjects, students, sessions, ...)."""
    engine, transport = await _make_client(seed_demo=True)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def analytics_client():
    """Seeded client that also includes the backdated session-analytics demo series
    (the data behind the student "My progress" charts)."""
    engine, transport = await _make_client(seed_demo=True, with_analytics=True)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()
