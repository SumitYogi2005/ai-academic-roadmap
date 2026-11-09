"""
Pydantic models for `syllabus_documents` and `syllabus_content` collections.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# ── Embedded sub-models ───────────────────────────────────────────────────────

class Topic(BaseModel):
    """A single topic inside a unit."""
    id: str = Field(description="Unique topic identifier (e.g. 'unit1_topic2')")
    name: str
    description: str = ""
    duration_hours: float = Field(default=1.0, ge=0)
    objectives: List[str] = Field(default_factory=list)


class Unit(BaseModel):
    """A unit (chapter / module) in the syllabus."""
    id: str = Field(description="Unique unit identifier")
    name: str
    description: str = ""
    topics: List[Topic] = Field(default_factory=list)
    sequence: int = Field(default=0, description="Order within the syllabus")


# ── Collection documents ──────────────────────────────────────────────────────

class SyllabusDocument(BaseModel):
    """Represents a row in `syllabus_documents`."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    subject_id: str = Field(description="Slug / short name of the subject")
    file_name: str
    storage_key: str = Field(description="Relative path under UPLOAD_DIR")
    mime_type: str
    size: int = Field(description="File size in bytes")
    status: DocumentStatus = DocumentStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data


class SyllabusContent(BaseModel):
    """Represents a row in `syllabus_content` (extracted & AI-parsed content)."""

    id: Optional[str] = Field(default=None, alias="_id")
    document_id: str
    raw_text: str = Field(default="", description="Normalised extracted text")
    units: List[Unit] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    ai_warnings: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data
