"""
AI assistant routes: chat, quiz generation, notes generation.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional

from app.core.security import get_current_user_id
from app.db.database import get_database
from app.repositories import roadmap_repository as rm_repo
from app.services.ai.provider import get_ai_provider
from app.services.ai.prompts import (
    explain_topic_prompt,
    generate_quiz_prompt,
    generate_notes_prompt,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    question: str
    node_id: Optional[str] = None
    roadmap_id: Optional[str] = None
    context: Optional[str] = None


class QuizRequest(BaseModel):
    node_id: str
    roadmap_id: str
    difficulty: str = "medium"
    num_questions: int = 5


class NotesRequest(BaseModel):
    node_id: str
    roadmap_id: str


@router.post("/chat")
async def chat(
    body: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Answer a student's question, optionally grounded in a specific topic."""
    topic_title = "General Question"
    topic_description = ""
    context = body.context or ""

    if body.node_id:
        node = await rm_repo.get_node_by_id(db, body.node_id)
        if node:
            # Verify ownership
            roadmap = await rm_repo.get_roadmap_by_id(db, node.get("roadmap_id", ""))
            if roadmap and roadmap.get("user_id") != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
            topic_title = node.get("title", "Topic")
            topic_description = node.get("description", "")

    provider = get_ai_provider()
    prompt = explain_topic_prompt(topic_title, topic_description, body.question, context)

    try:
        answer = await provider.generate_text(
            prompt,
            system="You are a helpful academic tutor. Provide clear, accurate, educational explanations.",
        )
    except Exception as exc:
        logger.error("AI chat error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again.",
        )

    return {
        "success": True,
        "data": {
            "question": body.question,
            "answer": answer,
            "topic": topic_title,
        },
    }


@router.post("/quiz")
async def generate_quiz(
    body: QuizRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate a multiple-choice quiz for a specific roadmap node."""
    node = await rm_repo.get_node_by_id(db, body.node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found.")
    roadmap = await rm_repo.get_roadmap_by_id(db, body.roadmap_id)
    if not roadmap or roadmap["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    provider = get_ai_provider()
    prompt = generate_quiz_prompt(
        node.get("title", "Topic"),
        node.get("description", ""),
        body.difficulty,
        body.num_questions,
    )

    try:
        result = await provider.generate_structured_output(prompt, schema={})
    except Exception as exc:
        logger.error("AI quiz error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable.",
        )

    return {
        "success": True,
        "data": {
            "node_id": body.node_id,
            "topic": node.get("title"),
            "questions": result.get("questions", []),
        },
    }


@router.post("/notes")
async def generate_notes(
    body: NotesRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate structured study notes for a roadmap node."""
    node = await rm_repo.get_node_by_id(db, body.node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found.")
    roadmap = await rm_repo.get_roadmap_by_id(db, body.roadmap_id)
    if not roadmap or roadmap["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    provider = get_ai_provider()
    prompt = generate_notes_prompt(
        node.get("title", "Topic"),
        node.get("description", ""),
        [],  # objectives could be added from syllabus content
    )

    try:
        result = await provider.generate_structured_output(prompt, schema={})
    except Exception as exc:
        logger.error("AI notes error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable.",
        )

    return {
        "success": True,
        "data": {
            "node_id": body.node_id,
            "topic": node.get("title"),
            "notes": result,
        },
    }
