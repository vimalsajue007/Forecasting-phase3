import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.core.config import settings

# Use in-memory SQLite for tests (no MySQL needed)
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the test session."""
    from app.models import user, dataset, forecast, notification, model_comparison
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fresh DB session per test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def client():
    """Test client with DB override."""
    import os
    os.makedirs("uploads", exist_ok=True)

    from main import app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def registered_user(client):
    """Register a user once and return credentials."""
    res = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test@1234",
        "full_name": "Test User",
    })
    assert res.status_code == 201
    return {"username": "testuser", "password": "Test@1234", "data": res.json()}


@pytest.fixture(scope="session")
def auth_headers(client, registered_user):
    """Login and return Authorization headers."""
    res = client.post("/api/auth/login", json={
        "username": registered_user["username"],
        "password": registered_user["password"],
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
