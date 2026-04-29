import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app, graphql_app, get_context
from app.database import Base, get_db
import app.models  # noqa: F401 — registers models on Base.metadata


@pytest_asyncio.fixture(scope="function")
async def db():
    """Create a fresh in-memory async SQLite DB for each test function."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db):
    async def override_get_db():
        yield db

    async def override_context(request, data):
        return {"request": request, "db": db}

    fastapi_app.dependency_overrides[get_db] = override_get_db
    graphql_app.http_handler.context_value = override_context
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        follow_redirects=True,
    ) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
    graphql_app.http_handler.context_value = get_context
