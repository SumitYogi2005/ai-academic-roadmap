"""
Pydantic request / response schemas for planner endpoints.
"""
from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.planner import PlanStatus, ProgressStatus, SessionStatus, SessionType


# ── Study Plan ────────────────────────────────────────────────────────────────

class StudyPlanRequest(BaseModel):
    roadmap_id: str
    start_date: date
    target_date: date
    # day-of-week (lowercase) -> available minutes per day
    availability: Dict[str, int] = Field(
        description='E.g. {"monday": 90, "tuesday": 60}',
        default_factory=dict,
    )

    model_config = {"json_encoders": {date: str}}


class SessionResponse(BaseModel):
    id: str
    plan_id: str
    node_id: str
    session_date: str  # ISO date string
    start_time: Optional[str]
    duration_minutes: int
    session_type: SessionType
    status: SessionStatus
    notes: str


class StudyPlanResponse(BaseModel):
    id: str
    user_id: str
    roadmap_id: str
    start_date: str
    target_date: str
    availability: Dict[str, int]
    status: PlanStatus
    version: int
    total_sessions: int
    completed_sessions: int
    sessions: List[SessionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


# ── Session update ────────────────────────────────────────────────────────────

class SessionStatusUpdate(BaseModel):
    status: SessionStatus
    notes: Optional[str] = None


# ── Progress ──────────────────────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    status: ProgressStatus
    completion_percentage: float = Field(ge=0.0, le=100.0)


class ProgressResponse(BaseModel):
    id: str
    user_id: str
    roadmap_id: str
    node_id: str
    status: ProgressStatus
    completion_percentage: float
    last_studied_at: Optional[datetime]
    updated_at: datetime


# ── Analytics ─────────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_roadmaps: int
    total_study_plans: int
    total_sessions: int
    completed_sessions: int
    total_nodes: int
    completed_nodes: int
    overall_completion_percentage: float
