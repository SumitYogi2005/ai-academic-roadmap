"""
User profile and preferences routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import List, Optional

from app.core.security import get_current_user_id
from app.db.database import get_database
from app.repositories import user_repository as user_repo

router = APIRouter(prefix="/users", tags=["Users"])


class PreferencesUpdate(BaseModel):
    study_hours_per_day: Optional[float] = None
    preferred_study_times: Optional[List[str]] = None
    learning_level: Optional[str] = None
    goal: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None


def _serialize_user(user: dict) -> dict:
    return {
        "id": user["_id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "preferences": user.get("preferences", {}),
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"],
    }


@router.get("/me")
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Return the authenticated student's profile."""
    user = await user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {"success": True, "data": _serialize_user(user)}


@router.put("/me")
async def update_profile(
    body: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update the student's profile information."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update.")
    user = await user_repo.update_user(db, user_id, updates)
    return {"success": True, "data": _serialize_user(user), "message": "Profile updated."}


@router.put("/preferences")
async def update_preferences(
    body: PreferencesUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update the student's study preferences."""
    updates_raw = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates_raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No preferences to update.")
    # Nest under preferences subdocument
    pref_updates = {f"preferences.{k}": v for k, v in updates_raw.items()}
    user = await user_repo.update_user(db, user_id, pref_updates)
    return {"success": True, "data": _serialize_user(user), "message": "Preferences updated."}
