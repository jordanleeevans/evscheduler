import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, graphql_app, get_context
from app.database import Base, get_db


@pytest.fixture(scope="function")
def db():
    """Create a fresh in-memory SQLite DB for each test function."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    async def override_context(request, data):
        return {"request": request, "db": db}

    app.dependency_overrides[get_db] = override_get_db
    graphql_app.http_handler.context_value = override_context
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    graphql_app.http_handler.context_value = get_context
