"""
Async CRUD operations for `syllabus_documents` and `syllabus_content` collections.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.document import SyllabusContent, SyllabusDocument

logger = logging.getLogger(__name__)

DOCS_COL = "syllabus_documents"
CONTENT_COL = "syllabus_content"


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ── SyllabusDocument CRUD ─────────────────────────────────────────────────────

async def create_document(db: AsyncIOMotorDatabase, document: SyllabusDocument) -> dict:
    data = document.to_mongo()
    result = await db[DOCS_COL].insert_one(data)
    created = await db[DOCS_COL].find_one({"_id": result.inserted_id})
    return _serialize(created)


async def get_document_by_id(db: AsyncIOMotorDatabase, doc_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return None
    doc = await db[DOCS_COL].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def get_documents_by_user(db: AsyncIOMotorDatabase, user_id: str) -> List[dict]:
    cursor = db[DOCS_COL].find({"user_id": user_id}).sort("created_at", -1)
    return [_serialize(d) async for d in cursor]


async def update_document_status(
    db: AsyncIOMotorDatabase,
    doc_id: str,
    status: str,
    error_message: Optional[str] = None,
) -> Optional[dict]:
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return None
    updates: dict = {"status": status, "updated_at": datetime.now(timezone.utc)}
    if error_message is not None:
        updates["error_message"] = error_message
    await db[DOCS_COL].update_one({"_id": oid}, {"$set": updates})
    return await get_document_by_id(db, doc_id)


async def delete_document(db: AsyncIOMotorDatabase, doc_id: str) -> bool:
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return False
    result = await db[DOCS_COL].delete_one({"_id": oid})
    return result.deleted_count > 0


# ── SyllabusContent CRUD ──────────────────────────────────────────────────────

async def upsert_content(db: AsyncIOMotorDatabase, content: SyllabusContent) -> dict:
    """Insert or replace the content document for a given document_id."""
    data = content.to_mongo()
    result = await db[CONTENT_COL].find_one_and_replace(
        {"document_id": content.document_id},
        data,
        upsert=True,
        return_document=True,
    )
    # find_one_and_replace may return pre-update doc; refetch to get latest
    fetched = await db[CONTENT_COL].find_one({"document_id": content.document_id})
    return _serialize(fetched)


async def get_content_by_document_id(db: AsyncIOMotorDatabase, document_id: str) -> Optional[dict]:
    doc = await db[CONTENT_COL].find_one({"document_id": document_id})
    return _serialize(doc) if doc else None


async def update_content(db: AsyncIOMotorDatabase, document_id: str, updates: dict) -> Optional[dict]:
    updates["updated_at"] = datetime.now(timezone.utc)
    await db[CONTENT_COL].update_one({"document_id": document_id}, {"$set": updates})
    return await get_content_by_document_id(db, document_id)
