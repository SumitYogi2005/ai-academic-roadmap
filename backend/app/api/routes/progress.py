"""
Topic progress and analytics routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional

from app.core.security import get_current_user_id
from app.db.database import get_database
from app.models.planner import TopicProgress
from app.repositories import planner_repository as plan_repo
from app.repositories import roadmap_repository as rm_repo

router = APIRouter(tags=["Progress"])


class ProgressUpdate(BaseModel):
    status: str  # not_started | in_progress | completed
    completion_percentage: Optional[int] = None
    roadmap_id: str


@router.put("/progress/{node_id}")
async def update_progress(
    node_id: str,
    body: ProgressUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update the student's progress for a specific roadmap node."""
    allowed = {"not_started", "in_progress", "completed"}
    if body.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Status must be one of: {allowed}",
        )

    pct = body.completion_percentage
    if pct is None:
        pct = 100 if body.status == "completed" else (50 if body.status == "in_progress" else 0)

    progress_doc = TopicProgress(
        user_id=user_id,
        roadmap_id=body.roadmap_id,
        node_id=node_id,
        status=body.status,
        completion_percentage=pct,
    )
    result = await plan_repo.upsert_progress(db, progress_doc)
    return {"success": True, "data": result, "message": "Progress updated."}


@router.get("/progress/roadmap/{roadmap_id}")
async def get_roadmap_progress(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get progress for all nodes in a roadmap."""
    roadmap = await rm_repo.get_roadmap_by_id(db, roadmap_id)
    if not roadmap or roadmap["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    progress_list = await plan_repo.get_progress_by_roadmap(db, user_id, roadmap_id)
    nodes = await rm_repo.get_nodes_by_roadmap(db, roadmap_id)
    total = len(nodes)
    completed = sum(1 for p in progress_list if p.get("status") == "completed")
    in_progress = sum(1 for p in progress_list if p.get("status") == "in_progress")

    return {
        "success": True,
        "data": {
            "roadmap_id": roadmap_id,
            "total_nodes": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": total - completed - in_progress,
            "completion_percentage": round((completed / total * 100) if total else 0, 1),
            "progress": progress_list,
        },
    }


@router.get("/analytics/summary")
async def get_analytics_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Return summary analytics for the student's dashboard."""
    from app.repositories import roadmap_repository as rm_repo
    from app.repositories import planner_repository as plan_repo

    roadmaps = await rm_repo.get_roadmaps_by_user(db, user_id)
    plans = await plan_repo.get_plans_by_user(db, user_id)

    total_nodes = 0
    total_completed = 0
    roadmap_summaries = []

    for rm in roadmaps:
        nodes = await rm_repo.get_nodes_by_roadmap(db, rm["_id"])
        completed = await plan_repo.count_completed_nodes(db, user_id, rm["_id"])
        total_nodes += len(nodes)
        total_completed += completed
        roadmap_summaries.append({
            "id": rm["_id"],
            "title": rm["title"],
            "type": rm["type"],
            "total_nodes": len(nodes),
            "completed_nodes": completed,
            "completion_percentage": round((completed / len(nodes) * 100) if nodes else 0, 1),
        })

    # Count today's sessions across all plans
    from datetime import date
    today_str = date.today().isoformat()
    today_sessions = 0
    for plan in plans:
        sessions = await plan_repo.get_sessions_by_plan(db, plan["_id"])
        today_sessions += sum(1 for s in sessions if s.get("session_date", "")[:10] == today_str)

    return {
        "success": True,
        "data": {
            "active_roadmaps": len([r for r in roadmaps if r.get("status") == "active"]),
            "total_nodes": total_nodes,
            "completed_nodes": total_completed,
            "overall_completion": round((total_completed / total_nodes * 100) if total_nodes else 0, 1),
            "today_sessions": today_sessions,
            "roadmaps": roadmap_summaries,
        },
    }
