"""
Async CRUD operations for the `users` MongoDB collection.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import UserDocument

logger = logging.getLogger(__name__)

COLLECTION = "users"


def _serialize(doc: dict) -> dict:
    """Convert ObjectId _id to string."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def create_user(db: AsyncIOMotorDatabase, user: UserDocument) -> dict:
    """Insert a new user and return the created document."""
    data = user.to_mongo()
    result = await db[COLLECTION].insert_one(data)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _serialize(created)


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[dict]:
    """Fetch a user by their ObjectId string. Returns None if not found."""
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    doc = await db[COLLECTION].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    """Fetch a user by email address (case-insensitive via index collation)."""
    doc = await db[COLLECTION].find_one({"email": email.lower().strip()})
    return _serialize(doc) if doc else None


async def update_user(db: AsyncIOMotorDatabase, user_id: str, updates: dict) -> Optional[dict]:
    """
    Apply *updates* (a partial dict) to the user document.
    Always sets `updated_at` to now.
    """
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    updates["updated_at"] = datetime.now(timezone.utc)
    await db[COLLECTION].update_one({"_id": oid}, {"$set": updates})
    return await get_user_by_id(db, user_id)


async def email_exists(db: AsyncIOMotorDatabase, email: str) -> bool:
    """Return True if an account with *email* already exists."""
    count = await db[COLLECTION].count_documents({"email": email.lower().strip()})
    return count > 0
