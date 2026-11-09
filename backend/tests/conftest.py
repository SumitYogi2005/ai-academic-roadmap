"""
Pytest configuration and shared fixtures for AI Academic Roadmap tests.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    """Create a FastAPI test client."""
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
async def clean_test_db():
    """Clean test database before each test."""
    from app.core.config import settings
    if "test" not in settings.MONGODB_DATABASE.lower():
        pytest.skip("Test database must have 'test' in its name for safety")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    # Drop all collections before each test
    collections = await db.list_collection_names()
    for col in collections:
        await db[col].drop()
    client.close()
    yield
