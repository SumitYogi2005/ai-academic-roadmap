"""
Pydantic request / response schemas for roadmap endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.roadmap import NodeDifficulty, NodeType, RoadmapStatus, RoadmapType, EdgeRelationship


# ── Requests ──────────────────────────────────────────────────────────────────

class AcademicRoadmapRequest(BaseModel):
    document_id: str = Field(description="ID of the verified SyllabusDocument")
    title: str = Field(min_length=3, max_length=200)
    goal: str = Field(default="", max_length=500)


class SkillRoadmapRequest(BaseModel):
    skill_name: str = Field(min_length=2, max_length=200)
    skill_level: str = Field(description="beginner | intermediate | advanced")
    goal: str = Field(default="", max_length=500)
    timeframe_weeks: int = Field(default=12, ge=1, le=104)


class NodePositionUpdate(BaseModel):
    position_x: float
    position_y: float


# ── Responses ─────────────────────────────────────────────────────────────────

class NodeResponse(BaseModel):
    id: str
    roadmap_id: str
    title: str
    description: str
    type: NodeType
    duration_hours: float
    difficulty: NodeDifficulty
    source_topic_id: Optional[str]
    position_x: float
    position_y: float


class EdgeResponse(BaseModel):
    id: str
    roadmap_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: EdgeRelationship


class RoadmapResponse(BaseModel):
    id: str
    user_id: str
    source_document_id: Optional[str]
    title: str
    type: RoadmapType
    goal: str
    skill_name: Optional[str]
    skill_level: Optional[str]
    status: RoadmapStatus
    version: int
    nodes: List[NodeResponse] = Field(default_factory=list)
    edges: List[EdgeResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class RoadmapListItem(BaseModel):
    id: str
    title: str
    type: RoadmapType
    status: RoadmapStatus
    goal: str
    created_at: datetime
