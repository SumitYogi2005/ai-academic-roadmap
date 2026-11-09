"""
Study planner routes: generate, retrieve, update sessions, reschedule.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.security import get_current_user_id
from app.db.database import get_database
from app.models.planner import StudyPlan, StudySession
from app.repositories import planner_repository as plan_repo
from app.repositories import roadmap_repository as rm_repo
from app.services.planner.scheduler import generate_study_plan, reschedule_plan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/study-plans", tags=["Study Planner"])


class GeneratePlanRequest(BaseModel):
    roadmap_id: str
    start_date: date
    target_date: date
    availability: Dict[str, int]  # e.g. {"monday": 120, "tuesday": 90, ...}


class UpdateSessionRequest(BaseModel):
    status: str  # pending | completed | missed | rescheduled


class RescheduleRequest(BaseModel):
    start_from: date
    availability: Optional[Dict[str, int]] = None


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_plan(
    body: GeneratePlanRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate a personalized study plan for a roadmap."""
    roadmap = await rm_repo.get_roadmap_by_id(db, body.roadmap_id)
    if not roadmap or roadmap["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    if body.target_date <= body.start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target date must be after start date.")

    nodes = await rm_repo.get_nodes_by_roadmap(db, body.roadmap_id)
    edges = await rm_repo.get_edges_by_roadmap(db, body.roadmap_id)

    result = generate_study_plan(
        nodes=nodes,
        edges=edges,
        start_date=body.start_date,
        target_date=body.target_date,
        availability=body.availability,
    )

    plan_doc = StudyPlan(
        user_id=user_id,
        roadmap_id=body.roadmap_id,
        start_date=datetime.combine(body.start_date, datetime.min.time()).replace(tzinfo=timezone.utc),
        target_date=datetime.combine(body.target_date, datetime.min.time()).replace(tzinfo=timezone.utc),
        availability=body.availability,
        status="active",
    )
    plan = await plan_repo.create_plan(db, plan_doc)
    plan_id = plan["_id"]

    # Persist sessions
    session_docs = [
        StudySession(
            plan_id=plan_id,
            node_id=s["node_id"],
            session_date=datetime.fromisoformat(s["session_date"]).replace(tzinfo=timezone.utc)
            if isinstance(s["session_date"], str) else s["session_date"],
            start_time=s.get("start_time", "09:00"),
            duration_minutes=s["duration_minutes"],
            session_type=s.get("session_type", "study"),
            status=s.get("status", "pending"),
        )
        for s in result["sessions"]
    ]
    sessions = await plan_repo.create_sessions(db, session_docs)

    return {
        "success": True,
        "data": {
            "plan": plan,
            "sessions_count": len(sessions),
            "feasibility_report": result["feasibility_report"],
            "stats": result.get("stats", {}),
        },
        "message": f"Study plan generated with {len(sessions)} sessions.",
    }


@router.get("")
async def list_plans(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List all study plans for the authenticated student."""
    plans = await plan_repo.get_plans_by_user(db, user_id)
    return {"success": True, "data": plans}


@router.get("/{plan_id}")
async def get_plan(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get a study plan with all its sessions."""
    plan = await plan_repo.get_plan_by_id(db, plan_id)
    if not plan or plan["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study plan not found.")
    sessions = await plan_repo.get_sessions_by_plan(db, plan_id)
    return {"success": True, "data": {"plan": plan, "sessions": sessions}}


@router.put("/{plan_id}/sessions/{session_id}")
async def update_session(
    plan_id: str,
    session_id: str,
    body: UpdateSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update a session's status (e.g. mark as completed or missed)."""
    plan = await plan_repo.get_plan_by_id(db, plan_id)
    if not plan or plan["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study plan not found.")

    allowed_statuses = {"pending", "completed", "missed", "rescheduled"}
    if body.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status. Must be one of: {allowed_statuses}",
        )

    updated = await plan_repo.update_session(db, session_id, {"status": body.status})
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return {"success": True, "data": updated, "message": "Session updated."}


@router.post("/{plan_id}/reschedule")
async def reschedule(
    plan_id: str,
    body: RescheduleRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Reschedule all pending/missed sessions from a given start date."""
    plan = await plan_repo.get_plan_by_id(db, plan_id)
    if not plan or plan["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study plan not found.")

    all_sessions = await plan_repo.get_sessions_by_plan(db, plan_id)
    availability = body.availability or plan.get("availability", {})

    target_date = plan["target_date"]
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date[:10])
    elif hasattr(target_date, "date"):
        target_date = target_date.date()

    new_sessions_data = reschedule_plan(
        remaining_sessions=[
            {"_id": s["_id"], "node_id": s["node_id"], "duration_minutes": s["duration_minutes"],
             "status": s["status"], "session_type": s.get("session_type", "study"),
             "title": s.get("title", "")}
            for s in all_sessions
        ],
        start_from=body.start_from,
        target_date=target_date,
        availability=availability,
    )

    # Mark old pending/missed sessions as rescheduled, insert new ones
    for s in all_sessions:
        if s["status"] in ("pending", "missed"):
            await plan_repo.update_session(db, s["_id"], {"status": "rescheduled"})

    new_docs = [
        StudySession(
            plan_id=plan_id,
            node_id=s["node_id"],
            session_date=datetime.fromisoformat(s["session_date"]).replace(tzinfo=timezone.utc),
            start_time=s.get("start_time", "09:00"),
            duration_minutes=s["duration_minutes"],
            session_type=s.get("session_type", "study"),
            status="pending",
        )
        for s in new_sessions_data
    ]
    new_sessions = await plan_repo.create_sessions(db, new_docs)

    return {
        "success": True,
        "data": {"rescheduled_count": len(new_sessions)},
        "message": f"Rescheduled {len(new_sessions)} sessions.",
    }
