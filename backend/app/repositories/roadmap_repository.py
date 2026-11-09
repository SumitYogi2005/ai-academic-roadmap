"""
Async CRUD operations for `roadmaps`, `roadmap_nodes`, and `roadmap_edges`.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.roadmap import Roadmap, RoadmapEdge, RoadmapNode

logger = logging.getLogger(__name__)

ROADMAPS_COL = "roadmaps"
NODES_COL = "roadmap_nodes"
EDGES_COL = "roadmap_edges"


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ── Roadmap CRUD ──────────────────────────────────────────────────────────────

async def create_roadmap(db: AsyncIOMotorDatabase, roadmap: Roadmap) -> dict:
    data = roadmap.to_mongo()
    result = await db[ROADMAPS_COL].insert_one(data)
    created = await db[ROADMAPS_COL].find_one({"_id": result.inserted_id})
    return _serialize(created)


async def get_roadmap_by_id(db: AsyncIOMotorDatabase, roadmap_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(roadmap_id)
    except Exception:
        return None
    doc = await db[ROADMAPS_COL].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def get_roadmaps_by_user(db: AsyncIOMotorDatabase, user_id: str) -> List[dict]:
    cursor = db[ROADMAPS_COL].find({"user_id": user_id}).sort("created_at", -1)
    return [_serialize(d) async for d in cursor]


async def update_roadmap(db: AsyncIOMotorDatabase, roadmap_id: str, updates: dict) -> Optional[dict]:
    try:
        oid = ObjectId(roadmap_id)
    except Exception:
        return None
    updates["updated_at"] = datetime.now(timezone.utc)
    await db[ROADMAPS_COL].update_one({"_id": oid}, {"$set": updates})
    return await get_roadmap_by_id(db, roadmap_id)


# ── RoadmapNode CRUD ──────────────────────────────────────────────────────────

async def create_nodes(db: AsyncIOMotorDatabase, nodes: List[RoadmapNode]) -> List[dict]:
    if not nodes:
        return []
    data = [n.to_mongo() for n in nodes]
    result = await db[NODES_COL].insert_many(data)
    inserted_ids = result.inserted_ids
    cursor = db[NODES_COL].find({"_id": {"$in": inserted_ids}})
    return [_serialize(d) async for d in cursor]


async def get_nodes_by_roadmap(db: AsyncIOMotorDatabase, roadmap_id: str) -> List[dict]:
    cursor = db[NODES_COL].find({"roadmap_id": roadmap_id})
    return [_serialize(d) async for d in cursor]


async def get_node_by_id(db: AsyncIOMotorDatabase, node_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(node_id)
    except Exception:
        return None
    doc = await db[NODES_COL].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def update_node(db: AsyncIOMotorDatabase, node_id: str, updates: dict) -> Optional[dict]:
    try:
        oid = ObjectId(node_id)
    except Exception:
        return None
    updates["updated_at"] = datetime.now(timezone.utc)
    await db[NODES_COL].update_one({"_id": oid}, {"$set": updates})
    return await get_node_by_id(db, node_id)


# ── RoadmapEdge CRUD ──────────────────────────────────────────────────────────

async def create_edges(db: AsyncIOMotorDatabase, edges: List[RoadmapEdge]) -> List[dict]:
    if not edges:
        return []
    data = [e.to_mongo() for e in edges]
    result = await db[EDGES_COL].insert_many(data)
    inserted_ids = result.inserted_ids
    cursor = db[EDGES_COL].find({"_id": {"$in": inserted_ids}})
    return [_serialize(d) async for d in cursor]


async def get_edges_by_roadmap(db: AsyncIOMotorDatabase, roadmap_id: str) -> List[dict]:
    cursor = db[EDGES_COL].find({"roadmap_id": roadmap_id})
    return [_serialize(d) async for d in cursor]
