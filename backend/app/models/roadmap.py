"""
Pydantic models for `roadmaps`, `roadmap_nodes`, and `roadmap_edges` collections.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class RoadmapType(str, Enum):
    ACADEMIC = "academic"
    SKILL = "skill"


class RoadmapStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class NodeType(str, Enum):
    CONCEPT = "concept"
    PRACTICE = "practice"
    PROJECT = "project"
    ASSESSMENT = "assessment"


class NodeDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EdgeRelationship(str, Enum):
    PREREQUISITE = "prerequisite"
    RELATED = "related"


# ── Collection documents ──────────────────────────────────────────────────────

class Roadmap(BaseModel):
    """Represents a document in `roadmaps`."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    source_document_id: Optional[str] = None  # only for academic roadmaps
    title: str
    type: RoadmapType
    goal: str = ""
    # Skill-roadmap specific fields
    skill_name: Optional[str] = None
    skill_level: Optional[str] = None
    status: RoadmapStatus = RoadmapStatus.DRAFT
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data


class RoadmapNode(BaseModel):
    """Represents a document in `roadmap_nodes`."""

    id: Optional[str] = Field(default=None, alias="_id")
    roadmap_id: str
    title: str
    description: str = ""
    type: NodeType = NodeType.CONCEPT
    duration_hours: float = Field(default=1.0, ge=0)
    difficulty: NodeDifficulty = NodeDifficulty.BEGINNER
    source_topic_id: Optional[str] = None
    # UI position (drag-and-drop)
    position_x: float = 0.0
    position_y: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data


class RoadmapEdge(BaseModel):
    """Represents a document in `roadmap_edges`."""

    id: Optional[str] = Field(default=None, alias="_id")
    roadmap_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: EdgeRelationship = EdgeRelationship.PREREQUISITE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data
