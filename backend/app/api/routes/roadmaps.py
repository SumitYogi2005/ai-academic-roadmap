"""
Roadmap generation and retrieval routes.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.security import get_current_user_id
from app.db.database import get_database
from app.models.roadmap import Roadmap, RoadmapEdge, RoadmapNode, RoadmapStatus, RoadmapType
from app.repositories import document_repository as doc_repo
from app.repositories import roadmap_repository as rm_repo
from app.services.roadmap.generator import (
    detect_prerequisite_cycles,
    generate_academic_roadmap,
    generate_skill_roadmap,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


# ── Request schemas ───────────────────────────────────────────────────────────

class AcademicRoadmapRequest(BaseModel):
    document_id: str
    title: Optional[str] = None
    goal: Optional[str] = ""


class SkillRoadmapRequest(BaseModel):
    skill_name: str
    skill_level: str = "beginner"
    goal: str = ""
    timeframe_weeks: int = 8
    title: Optional[str] = None


class NodePositionUpdate(BaseModel):
    position_x: float
    position_y: float


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _insert_nodes_and_edges(
    db, roadmap_id: str, nodes_raw: list[dict], edges_raw: list[dict]
) -> tuple[list[dict], list[dict]]:
    """
    Insert nodes first, build ID map, then insert edges with real node IDs.
    Returns (inserted_nodes, inserted_edges).
    """
    # Insert nodes
    node_docs = [RoadmapNode(**{**n, "roadmap_id": roadmap_id}) for n in nodes_raw]
    inserted_nodes = await rm_repo.create_nodes(db, node_docs)

    # Build mapping: source_topic_id -> _id  AND  index -> _id
    topic_to_id: dict[str, str] = {}
    for i, node in enumerate(inserted_nodes):
        if node.get("source_topic_id"):
            topic_to_id[node["source_topic_id"]] = node["_id"]
        topic_to_id[str(i)] = node["_id"]

    # Resolve edges
    edge_docs = []
    for e in edges_raw:
        # Academic edges use source_topic_id/target_topic_id
        src_id = topic_to_id.get(e.get("source_topic_id", ""))
        tgt_id = topic_to_id.get(e.get("target_topic_id", ""))
        # Skill edges use source_index/target_index
        if not src_id:
            src_id = topic_to_id.get(str(e.get("source_index", "")))
        if not tgt_id:
            tgt_id = topic_to_id.get(str(e.get("target_index", "")))

        if src_id and tgt_id and src_id != tgt_id:
            edge_docs.append(RoadmapEdge(
                roadmap_id=roadmap_id,
                source_node_id=src_id,
                target_node_id=tgt_id,
                relationship_type=e.get("relationship_type", "prerequisite"),
            ))

    inserted_edges: list[dict] = []
    if edge_docs:
        # Cycle check
        edge_dicts = [
            {"source_node_id": ed.source_node_id, "target_node_id": ed.target_node_id,
             "relationship_type": ed.relationship_type}
            for ed in edge_docs
        ]
        if detect_prerequisite_cycles(edge_dicts):
            logger.warning("Prerequisite cycle detected – edges will be inserted without the cyclic ones")
            # Remove edges that cause cycles (simple: remove all prerequisites)
            edge_docs = [ed for ed in edge_docs if ed.relationship_type != "prerequisite"]

        inserted_edges = await rm_repo.create_edges(db, edge_docs)

    return inserted_nodes, inserted_edges


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/academic", status_code=status.HTTP_201_CREATED)
async def create_academic_roadmap(
    body: AcademicRoadmapRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate an academic roadmap from a verified syllabus document."""
    doc = await doc_repo.get_document_by_id(db, body.document_id)
    if not doc or doc["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if doc["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document processing is not complete.",
        )

    content = await doc_repo.get_content_by_document_id(db, body.document_id)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Syllabus content not found.")
    if content.get("verification_status") not in ("verified", "pending"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please review and confirm the extracted syllabus first.",
        )

    # Create roadmap record
    roadmap_doc = Roadmap(
        user_id=user_id,
        source_document_id=body.document_id,
        title=body.title or f"{doc['file_name']} Roadmap",
        type=RoadmapType.ACADEMIC,
        goal=body.goal or "",
        status=RoadmapStatus.ACTIVE,
    )
    roadmap = await rm_repo.create_roadmap(db, roadmap_doc)
    roadmap_id = roadmap["_id"]

    # Generate nodes and edges
    syllabus_data = {"subject": doc.get("subject_id", ""), "units": content.get("units", [])}
    nodes_raw, edges_raw = await generate_academic_roadmap(syllabus_data, roadmap_id)
    inserted_nodes, inserted_edges = await _insert_nodes_and_edges(db, roadmap_id, nodes_raw, edges_raw)

    return {
        "success": True,
        "data": {
            "roadmap": roadmap,
            "nodes": inserted_nodes,
            "edges": inserted_edges,
        },
        "message": f"Academic roadmap created with {len(inserted_nodes)} nodes.",
    }


@router.post("/skill", status_code=status.HTTP_201_CREATED)
async def create_skill_roadmap(
    body: SkillRoadmapRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate a skill development roadmap."""
    roadmap_doc = Roadmap(
        user_id=user_id,
        title=body.title or f"{body.skill_name} Learning Roadmap",
        type=RoadmapType.SKILL,
        goal=body.goal,
        skill_name=body.skill_name,
        skill_level=body.skill_level,
        status=RoadmapStatus.ACTIVE,
    )
    roadmap = await rm_repo.create_roadmap(db, roadmap_doc)
    roadmap_id = roadmap["_id"]

    nodes_raw, edges_raw = await generate_skill_roadmap(
        body.skill_name, body.skill_level, body.goal, body.timeframe_weeks, roadmap_id
    )
    inserted_nodes, inserted_edges = await _insert_nodes_and_edges(db, roadmap_id, nodes_raw, edges_raw)

    return {
        "success": True,
        "data": {
            "roadmap": roadmap,
            "nodes": inserted_nodes,
            "edges": inserted_edges,
        },
        "message": f"Skill roadmap created with {len(inserted_nodes)} nodes.",
    }


@router.get("")
async def list_roadmaps(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List all roadmaps for the authenticated student."""
    roadmaps = await rm_repo.get_roadmaps_by_user(db, user_id)
    # Enrich with node counts
    result = []
    for rm in roadmaps:
        nodes = await rm_repo.get_nodes_by_roadmap(db, rm["_id"])
        result.append({**rm, "node_count": len(nodes)})
    return {"success": True, "data": result}


@router.get("/{roadmap_id}")
async def get_roadmap(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get a roadmap with all its nodes and edges."""
    roadmap = await rm_repo.get_roadmap_by_id(db, roadmap_id)
    if not roadmap or roadmap["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    nodes = await rm_repo.get_nodes_by_roadmap(db, roadmap_id)
    edges = await rm_repo.get_edges_by_roadmap(db, roadmap_id)

    return {
        "success": True,
        "data": {
            "roadmap": roadmap,
            "nodes": nodes,
            "edges": edges,
        },
    }


@router.put("/{roadmap_id}/nodes/{node_id}")
async def update_node_position(
    roadmap_id: str,
    node_id: str,
    body: NodePositionUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update a node's canvas position (for drag-and-drop in the roadmap editor)."""
    roadmap = await rm_repo.get_roadmap_by_id(db, roadmap_id)
    if not roadmap or roadmap["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    updated = await rm_repo.update_node(db, node_id, {
        "position_x": body.position_x,
        "position_y": body.position_y,
    })
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found.")
    return {"success": True, "data": updated}
