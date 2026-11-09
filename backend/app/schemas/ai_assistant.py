"""
Pydantic request / response schemas for the AI assistant endpoints.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1)
    topic: Optional[str] = None
    context: Optional[str] = None
    roadmap_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    usage: Optional[Dict[str, int]] = None


# ── Quiz ──────────────────────────────────────────────────────────────────────

class QuizRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)
    difficulty: str = Field(default="intermediate", description="beginner | intermediate | advanced")
    num_questions: int = Field(default=5, ge=1, le=20)
    node_id: Optional[str] = None


class QuizOption(BaseModel):
    key: str   # "A", "B", "C", "D"
    text: str


class QuizQuestion(BaseModel):
    question: str
    options: List[QuizOption]
    correct_key: str
    explanation: str


class QuizResponse(BaseModel):
    topic: str
    difficulty: str
    questions: List[QuizQuestion]


# ── Notes ─────────────────────────────────────────────────────────────────────

class NotesRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)
    objectives: List[str] = Field(default_factory=list)
    node_id: Optional[str] = None
    style: str = Field(
        default="concise",
        description="'concise' | 'detailed' | 'bullet'",
    )


class NotesResponse(BaseModel):
    topic: str
    notes: str
    key_concepts: List[str]
