"""
Async CRUD operations for `study_plans`, `study_sessions`, and `topic_progress`.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.planner import StudyPlan, StudySession, TopicProgress

logger = logging.getLogger(__name__)

PLANS_COL = "study_plans"
SESSIONS_COL = "study_sessions"
PROGRESS_COL = "topic_progress"


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ── StudyPlan CRUD ────────────────────────────────────────────────────────────

async def create_plan(db: AsyncIOMotorDatabase, plan: StudyPlan) -> dict:
    data = plan.to_mongo()
    result = await db[PLANS_COL].insert_one(data)
    created = await db[PLANS_COL].find_one({"_id": result.inserted_id})
    return _serialize(created)


async def get_plan_by_id(db: AsyncIOMotorDatabase, plan_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(plan_id)
    except Exception:
        return None
    doc = await db[PLANS_COL].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def get_plans_by_user(db: AsyncIOMotorDatabase, user_id: str) -> List[dict]:
    cursor = db[PLANS_COL].find({"user_id": user_id}).sort("created_at", -1)
    return [_serialize(d) async for d in cursor]


async def update_plan(db: AsyncIOMotorDatabase, plan_id: str, updates: dict) -> Optional[dict]:
    try:
        oid = ObjectId(plan_id)
    except Exception:
        return None
    updates["updated_at"] = datetime.now(timezone.utc)
    await db[PLANS_COL].update_one({"_id": oid}, {"$set": updates})
    return await get_plan_by_id(db, plan_id)


# ── StudySession CRUD ─────────────────────────────────────────────────────────

async def create_sessions(db: AsyncIOMotorDatabase, sessions: List[StudySession]) -> List[dict]:
    if not sessions:
        return []
    data = [s.to_mongo() for s in sessions]
    result = await db[SESSIONS_COL].insert_many(data)
    inserted_ids = result.inserted_ids
    cursor = db[SESSIONS_COL].find({"_id": {"$in": inserted_ids}})
    return [_serialize(d) async for d in cursor]


async def get_sessions_by_plan(db: AsyncIOMotorDatabase, plan_id: str) -> List[dict]:
    cursor = db[SESSIONS_COL].find({"plan_id": plan_id}).sort("session_date", 1)
    return [_serialize(d) async for d in cursor]


async def get_session_by_id(db: AsyncIOMotorDatabase, session_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(session_id)
    except Exception:
        return None
    doc = await db[SESSIONS_COL].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def update_session(db: AsyncIOMotorDatabase, session_id: str, updates: dict) -> Optional[dict]:
    try:
        oid = ObjectId(session_id)
    except Exception:
        return None
    updates["updated_at"] = datetime.now(timezone.utc)
    await db[SESSIONS_COL].update_one({"_id": oid}, {"$set": updates})
    return await get_session_by_id(db, session_id)


async def delete_sessions_by_plan(db: AsyncIOMotorDatabase, plan_id: str) -> int:
    result = await db[SESSIONS_COL].delete_many({"plan_id": plan_id})
    return result.deleted_count


# ── TopicProgress CRUD ────────────────────────────────────────────────────────

async def upsert_progress(
    db: AsyncIOMotorDatabase, progress: TopicProgress
) -> dict:
    """Insert or update progress for a (user_id, node_id) pair."""
    data = progress.to_mongo()
    data["updated_at"] = datetime.now(timezone.utc)
    doc = await db[PROGRESS_COL].find_one_and_replace(
        {"user_id": progress.user_id, "node_id": progress.node_id},
        data,
        upsert=True,
        return_document=True,
    )
    # Refetch to ensure we have the latest
    fetched = await db[PROGRESS_COL].find_one(
        {"user_id": progress.user_id, "node_id": progress.node_id}
    )
    return _serialize(fetched)


async def get_progress_by_roadmap(
    db: AsyncIOMotorDatabase, user_id: str, roadmap_id: str
) -> List[dict]:
    cursor = db[PROGRESS_COL].find({"user_id": user_id, "roadmap_id": roadmap_id})
    return [_serialize(d) async for d in cursor]


async def get_progress_by_node(
    db: AsyncIOMotorDatabase, user_id: str, node_id: str
) -> Optional[dict]:
    doc = await db[PROGRESS_COL].find_one({"user_id": user_id, "node_id": node_id})
    return _serialize(doc) if doc else None


async def count_completed_nodes(
    db: AsyncIOMotorDatabase, user_id: str, roadmap_id: str
) -> int:
    return await db[PROGRESS_COL].count_documents(
        {"user_id": user_id, "roadmap_id": roadmap_id, "status": "completed"}
    )
