"""
Pydantic request / response schemas for document endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus, VerificationStatus


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    status: DocumentStatus
    created_at: datetime


# ── Extraction status ─────────────────────────────────────────────────────────

class ExtractionStatus(BaseModel):
    document_id: str
    status: DocumentStatus
    error_message: Optional[str] = None


# ── Syllabus review ───────────────────────────────────────────────────────────

class TopicData(BaseModel):
    id: str
    name: str
    description: str = ""
    duration_hours: float = 1.0
    objectives: List[str] = Field(default_factory=list)


class UnitData(BaseModel):
    id: str
    name: str
    description: str = ""
    topics: List[TopicData] = Field(default_factory=list)
    sequence: int = 0


class SyllabusReviewData(BaseModel):
    document_id: str
    units: List[UnitData]
    verification_status: VerificationStatus
    ai_warnings: List[str]


# ── Update requests ───────────────────────────────────────────────────────────

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    objectives: Optional[List[str]] = None


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None
    topics: Optional[List[TopicData]] = None
