"""
Pydantic models for `study_plans`, `study_sessions`, and `topic_progress` collections.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class PlanStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"
    RESCHEDULED = "rescheduled"


class SessionType(str, Enum):
    STUDY = "study"
    REVIEW = "review"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"


class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ── Collection documents ──────────────────────────────────────────────────────

class StudyPlan(BaseModel):
    """Represents a document in `study_plans`."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    roadmap_id: str
    start_date: date
    target_date: date
    # day-of-week -> available minutes (e.g. {"monday": 90, "tuesday": 60, ...})
    availability: Dict[str, int] = Field(default_factory=dict)
    status: PlanStatus = PlanStatus.ACTIVE
    version: int = 1
    total_sessions: int = 0
    completed_sessions: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        # Convert date/time objects to ISO strings for Mongo
        data["start_date"] = str(data["start_date"])
        data["target_date"] = str(data["target_date"])
        return data


class StudySession(BaseModel):
    """Represents a document in `study_sessions`."""

    id: Optional[str] = Field(default=None, alias="_id")
    plan_id: str
    node_id: str
    session_date: date
    start_time: Optional[time] = None
    duration_minutes: int = Field(ge=5)
    session_type: SessionType = SessionType.STUDY
    status: SessionStatus = SessionStatus.PENDING
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        data["session_date"] = str(data["session_date"])
        if data.get("start_time"):
            data["start_time"] = str(data["start_time"])
        return data


class TopicProgress(BaseModel):
    """Represents a document in `topic_progress`."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    roadmap_id: str
    node_id: str
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    last_studied_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data
