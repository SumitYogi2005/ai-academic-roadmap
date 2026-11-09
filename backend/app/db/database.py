"""
Async MongoDB client management using Motor.
Provides startup/shutdown lifecycle and collection accessors.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level client / db handles (set during startup)
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """Create the Motor client and verify the connection."""
    global _client, _db
    logger.info("Connecting to MongoDB at %s …", settings.MONGODB_URL)
    _client = AsyncIOMotorClient(settings.MONGODB_URL)
    _db = _client[settings.MONGODB_DATABASE]
    # Verify connectivity
    await _client.admin.command("ping")
    logger.info("MongoDB connected – database: %s", settings.MONGODB_DATABASE)
    await _create_indexes()


async def close_mongo_connection() -> None:
    """Close the Motor client."""
    global _client, _db
    if _client is not None:
        _client.close()
        logger.info("MongoDB connection closed.")
    _client = None
    _db = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database handle. Must be called after startup."""
    if _db is None:
        raise RuntimeError("Database is not connected. Call connect_to_mongo() first.")
    return _db


# ── Index creation ────────────────────────────────────────────────────────────

async def _create_indexes() -> None:
    """Create all required indexes on first startup (idempotent)."""
    db = get_database()

    # users
    await db["users"].create_index("email", unique=True)

    # syllabus_documents
    await db["syllabus_documents"].create_index("user_id")
    await db["syllabus_documents"].create_index("subject_id")

    # syllabus_content
    await db["syllabus_content"].create_index("document_id", unique=True)

    # roadmaps
    await db["roadmaps"].create_index("user_id")
    await db["roadmaps"].create_index("source_document_id")

    # roadmap_nodes
    await db["roadmap_nodes"].create_index("roadmap_id")

    # roadmap_edges
    await db["roadmap_edges"].create_index("roadmap_id")
    await db["roadmap_edges"].create_index([("source_node_id", 1), ("target_node_id", 1)])

    # study_plans
    await db["study_plans"].create_index("user_id")
    await db["study_plans"].create_index("roadmap_id")

    # study_sessions
    await db["study_sessions"].create_index("plan_id")
    await db["study_sessions"].create_index("node_id")
    await db["study_sessions"].create_index("session_date")

    # topic_progress
    await db["topic_progress"].create_index([("user_id", 1), ("node_id", 1)], unique=True)
    await db["topic_progress"].create_index("roadmap_id")

    logger.info("MongoDB indexes ensured.")


# ── Lifespan context manager (for FastAPI) ────────────────────────────────────

@asynccontextmanager
async def lifespan(app) -> AsyncGenerator[None, None]:  # type: ignore[type-arg]
    """FastAPI lifespan: connect on startup, disconnect on shutdown."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()
